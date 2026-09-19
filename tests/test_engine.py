import copy
import json
import unittest
from decimal import Decimal, localcontext
from pathlib import Path

from futures_lab.data.calendar import Calendar
from futures_lab.data.input import decode
from futures_lab.domain.events import canonical
from futures_lab.domain.values import DataError
from futures_lab.engine import Engine, evaluate_document
from futures_lab.rules.manifest import load_rules

ROOT = Path(__file__).resolve().parents[1]


def trace():
    return json.loads((ROOT / 'tests/fixtures/round_trip.json').read_text())


def rules():
    return load_rules(ROOT / 'rules/ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.3.yaml')


def make_engine(document=None):
    d = document or trace()
    return Engine(rules(), Calendar.parse(d['calendar']), d['provenance'],
                  run_id='unit-run', code_version='test', input_sha256='a' * 64)


def evaluate(d):
    return evaluate_document(d, rules(), input_sha256='a' * 64, code_version='test')


class EngineTests(unittest.TestCase):
    def test_synthetic_round_trip_exact_checkpoints(self):
        d = trace(); result = evaluate(d)
        reports = {r['as_of_event_id']: r for r in result['checkpoints']}
        self.assertTrue(all(x['disposition'] == 'accepted' for x in result['dispositions']))
        for expected in d['expected_checkpoints']:
            actual = reports[expected['after_event_id']]
            self.assertEqual({k: actual[k] for k in expected if k != 'after_event_id'},
                             {k: v for k, v in expected.items() if k != 'after_event_id'})
        self.assertEqual(result['report']['state'], 'not_yet_eligible')
        self.assertEqual(result['report']['data_quality_reasons'], [])

    def test_duplicate_reimport_is_noop_and_snapshot_cannot_mutate_history(self):
        d = trace(); engine = make_engine()
        for e in d['events']:
            engine.append(e)
        before = canonical(engine.report()); history = engine.events
        for e in d['events']:
            self.assertEqual(engine.append(e)['disposition'], 'duplicate')
        self.assertEqual(canonical(engine.report()), before)
        report = engine.report(); report['exposure']['classes']['mini'] = '999'
        self.assertEqual(canonical(engine.report()), before)
        self.assertEqual(engine.events, history)

    def test_same_input_is_byte_stable_even_with_altered_decimal_context(self):
        first = canonical(evaluate(trace()))
        with localcontext() as c:
            c.prec = 3
            second = canonical(evaluate(trace()))
        self.assertEqual(first, second)

    def test_floor_moves_at_derived_next_session_start_only(self):
        engine = make_engine()
        for e in trace()['events']:
            engine.append(e)
        self.assertEqual(engine.report()['floor'], '48000.00')
        advanced = engine.advance_to('2026-09-17T22:00:00Z')
        self.assertEqual(advanced['floor'], '48095.00')
        self.assertEqual(advanced['session_id'], '2026-09-18')
        self.assertFalse(advanced['after_session_close'])
        self.assertEqual(len(engine.events), 13)
        with self.assertRaisesRegex(DataError, 'clock_reversal'):
            engine.advance_to('2026-09-17T19:00:00Z')

    def test_observed_drawdown_contact_is_permanent_after_recovery(self):
        for commission, breach in [('1999.99', False), ('2000.00', True), ('2000.01', True)]:
            with self.subTest(commission=commission):
                d = trace(); d['events'][5]['payload']['amount'] = commission
                result = evaluate(d)
                self.assertEqual(result['report']['drawdown_breached'], breach)
                self.assertEqual(result['report']['state'] == 'breached', breach)
                self.assertEqual(result['report']['breach_evidence_event_ids'], ['synthetic-event-006'] if breach else [])

    def test_unrealized_loss_causes_contact_and_breach_survives_flattening(self):
        d = trace()
        for i in (6, 7):
            d['events'][i]['payload']['price'] = '60.00'
        result = evaluate(d)['report']
        self.assertEqual(result['balance'], '50095.00')
        self.assertTrue(result['drawdown_breached'])
        self.assertIn('synthetic-event-008', result['breach_evidence_event_ids'])

    def test_observed_exposure_excess_preserved_without_permanent_breach(self):
        for counting_class, quantity, weight in [('standard', 6, '1.0'), ('micro', 51, '0.1')]:
            with self.subTest(counting_class=counting_class):
                d = trace(); d['events'][0]['payload'].update(ftmo_counting_class=counting_class, mini_equivalent=weight)
                for e in d['events']:
                    if 'quantity' in e['payload']:
                        e['payload']['quantity'] = quantity
                result = evaluate(d)['report']
                self.assertEqual(result['open_positions'], 0)
                self.assertTrue(result['exposure']['within_cap'])
                self.assertEqual(result['exposure']['policy_status'], 'MANUAL_REVIEW')
                self.assertEqual(result['state'], 'data_unavailable')
                self.assertIn('exposure_consequence_unresolved', result['data_quality_reasons'])
                self.assertFalse(result['drawdown_breached'])
                self.assertIn('synthetic-event-005', result['exposure']['evidence_event_ids'])

    def test_partial_fills_track_remaining_order_quantity(self):
        d = trace(); engine = make_engine()
        for e in d['events'][:4]:
            if e['event_type'] == 'OrderIntent':
                e['payload']['quantity'] = 3
            engine.append(e)
        fill = d['events'][4]; fill['payload']['quantity'] = 1
        self.assertEqual(engine.append(fill)['disposition'], 'accepted')
        fill = copy.deepcopy(fill); fill.update(event_id='partial-2', source_event_id='partial-2', sequence=6)
        fill['payload'].update(fill_id='fill-2', quantity=2, price='101.00')
        self.assertEqual(engine.append(fill)['disposition'], 'accepted')
        self.assertEqual(engine.report()['positions'][0]['quantity'], 3)
        fill = copy.deepcopy(fill); fill.update(event_id='overfill', source_event_id='overfill', sequence=7)
        fill['payload'].update(fill_id='fill-3', quantity=1)
        self.assertEqual(engine.append(fill)['reason'], 'overfilled_order')
        self.assertEqual(engine.report()['positions'][0]['quantity'], 3)

    def test_missing_marks_do_not_silently_use_stale_prices(self):
        d = trace(); d['events'][5]['timestamp_utc'] = '2026-09-17T14:00:02Z'
        result = evaluate(d)
        fee = next(r for r in result['checkpoints'] if r['as_of_event_id'] == 'synthetic-event-006')
        self.assertIsNone(fee['equity'])
        self.assertEqual(fee['balance'], '49997.50')
        self.assertFalse(fee['drawdown_breached'])
        self.assertEqual(result['report']['state'], 'data_unavailable')
        self.assertIn('incomplete_valuation_history', result['report']['data_quality_reasons'])

    def test_calendar_gap_close_boundary_and_malformed_event_quarantine(self):
        for stamp in ['2026-09-17T20:10:00Z', '2026-09-17T20:11:00Z']:
            d = trace(); d['events'][4]['timestamp_utc'] = stamp
            result = evaluate(d)
            self.assertEqual(result['dispositions'][4]['disposition'], 'quarantine')
            self.assertEqual(result['report']['state'], 'data_unavailable')
        d = trace(); d['events'][4]['payload']['price'] = 100.0
        self.assertEqual(evaluate(d)['report']['state'], 'data_unavailable')

    def test_missing_provenance_and_calendar_are_explicit(self):
        for key in ('provenance', 'calendar'):
            d = trace(); del d[key]
            result = evaluate(d)
            self.assertEqual(result['report']['state'], 'data_unavailable')
            self.assertEqual(result['report']['ruleset_sha256'], rules().sha256)

    def test_quarantine_does_not_erase_existing_breach(self):
        d = trace(); d['events'][5]['payload']['amount'] = '2000.00'
        d['events'][7]['payload']['price'] = '101.01'
        result = evaluate(d)['report']
        self.assertEqual(result['state'], 'breached')
        self.assertTrue(result['quarantine'])
        self.assertTrue(result['drawdown_breached'])

    def test_json_duplicates_nonfinite_unknown_fields_and_corrections(self):
        for raw in [b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}']:
            with self.assertRaises(DataError):
                decode(raw)
        for change in [{'event_type': 'Correction'}, {'extra': 'unexpected'}]:
            d = trace(); d['events'][4].update(change)
            self.assertEqual(evaluate(d)['dispositions'][4]['disposition'], 'quarantine')

    def test_order_rejection_cannot_receive_fill(self):
        d = trace(); d['events'][3]['event_type'] = 'OrderRejected'
        d['events'][3]['payload']['reason_code'] = 'synthetic_rejection'
        self.assertEqual(evaluate(d)['dispositions'][4]['reason'], 'fill_without_acceptance')

    def test_expected_fixture_outputs_are_never_trusted_as_inputs(self):
        d = trace(); first = evaluate(d)
        d['expected_checkpoints'] = [{'equity': '100000000.00'}]
        self.assertEqual(evaluate(d), first)

    def test_calendar_explicit_early_close_and_missing_session_close(self):
        d = trace(); d['calendar']['sessions'][0]['close_utc'] = '2026-09-17T17:00:00Z'
        d['events'][-1]['timestamp_utc'] = '2026-09-17T17:00:00Z'
        self.assertEqual(evaluate(d)['report']['state'], 'not_yet_eligible')
        engine = make_engine()
        for e in trace()['events'][:-1]:
            engine.append(e)
        with self.assertRaisesRegex(DataError, 'missing_session_close'):
            engine.advance_to('2026-09-17T22:00:00Z')

    def test_multiple_commission_components_charge_once_per_event(self):
        d = trace(); engine = make_engine()
        for e in d['events'][:6]:
            engine.append(e)
        extra = copy.deepcopy(d['events'][5]); extra.update(event_id='exchange-fee', source_event_id='exchange-fee', sequence=7)
        extra['payload']['amount'] = '1.00'
        engine.append(extra); engine.append(extra)
        self.assertEqual(engine.report()['fees'], '3.50')
        self.assertEqual(engine.report()['balance'], '49996.50')
