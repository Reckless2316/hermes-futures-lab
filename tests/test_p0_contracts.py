"""P0 contract checks. Financial outcomes are reference data until P1."""

import copy
import hashlib
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from jsonschema import ValidationError

from scripts import verify_p0_artifacts as artifacts


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.manifest = artifacts.read_artifact(artifacts.ROOT / artifacts.ACTIVE_RULES)
        self.trace = artifacts.read_artifact(artifacts.ROOT / 'tests/fixtures/round_trip.json')
        self.reference = artifacts.read_artifact(artifacts.ROOT / 'tests/fixtures/growth_50k_reference.json')
        self.rules_hash = hashlib.sha256((artifacts.ROOT / artifacts.ACTIVE_RULES).read_bytes()).hexdigest()

    def test_complete_artifact_inventory_and_links(self):
        artifacts.main()

    def test_candidate_one_is_byte_identical_to_checkpoint(self):
        self.assertEqual(hashlib.sha256((artifacts.ROOT / artifacts.HISTORICAL_RULES).read_bytes()).hexdigest(),
                         artifacts.HISTORICAL_HASH)

    def test_candidate_two_is_byte_identical_to_reviewed_head(self):
        self.assertEqual(hashlib.sha256((artifacts.ROOT / artifacts.CANDIDATE_TWO_RULES).read_bytes()).hexdigest(),
                         artifacts.CANDIDATE_TWO_HASH)

    def test_candidate_three_records_lab_convention_and_unresolved_official_semantics(self):
        self.assertEqual(self.manifest['review_status'], 'pending')
        self.assertEqual(self.manifest['consistency']['decision_status'], 'human_accepted_lab_convention')
        self.assertEqual(self.manifest['consistency']['pending_decision'], 'FTMO_consistency_fee_basis')
        self.assertEqual(self.manifest['consistency']['required_reports'],
                         ['gross_consistency_share', 'net_of_fees_consistency_share'])
        self.assertFalse(self.manifest['consistency']['allow_silent_substitution'])
        self.assertEqual(self.manifest['consistency']['consistency_profit_basis'],
                         'realized_gross_pnl_minus_all_fees_posted_in_session')
        self.assertEqual(self.manifest['verified_on'], '2026-09-17')

    def test_manifest_rejects_wrong_types_unknown_fields_and_mixed_versions(self):
        mutations = [({'profit_target': 3000.0}), ({'profit_target': 'NaN'}),
                     ({'extra': 'unknown'}), ({'review_status': 'approved'}),
                     ({'daily_loss': '1000.00'}), ({'stage': 'sim_funded'}),
                     ({'rules_version': '2026-09-17-candidate.1'}),
                     ({'consistency': {**self.manifest['consistency'], 'consistency_profit_basis': None}})]
        for patch in mutations:
            with self.subTest(patch=patch), self.assertRaises(ValidationError):
                artifacts.validate_schema({**self.manifest, **patch}, 'rules/schema.json')

    def test_trace_rejects_invalid_money_times_fields_and_quantities(self):
        for label, index, field, value, payload in [
            ('float-price', 4, 'price', 100.0, True),
            ('nonfinite', 4, 'price', 'NaN', True),
            ('exponent', 4, 'price', '1e2', True),
            ('newline-price', 4, 'price', '100.00\n', True),
            ('zero-quantity', 4, 'quantity', 0, True),
            ('boolean-quantity', 4, 'quantity', True, True),
            ('fractional-quantity', 4, 'quantity', 1.5, True),
            ('extra-payload', 4, 'secret', 'unexpected', True),
            ('negative-fee', 5, 'amount', '-2.50', True),
            ('naive-time', 4, 'timestamp_utc', '2026-09-17T14:00:01', False),
            ('invalid-date', 4, 'timestamp_utc', '2026-02-30T14:00:01Z', False),
            ('invalid-separator', 4, 'timestamp_utc', '2026-09-17 14:00:01Z', False),
            ('unknown-type', 4, 'event_type', 'ExecuteRealOrder', False),
        ]:
            with self.subTest(label=label):
                trace = copy.deepcopy(self.trace)
                target = trace['events'][index]['payload'] if payload else trace['events'][index]
                target[field] = value
                with self.assertRaises(ValidationError):
                    artifacts.validate_trace(trace, self.manifest, self.rules_hash)

    def test_trace_rejects_broken_references_and_ordering(self):
        cases = [
            (4, 'event_id', self.trace['events'][3]['event_id'], False),
            (4, 'source_event_id', self.trace['events'][3]['source_event_id'], False),
            (4, 'sequence', 99, False),
            (4, 'timestamp_utc', '2026-09-17T12:00:00Z', False),
            (4, 'timestamp_utc', '2026-09-17T20:10:00Z', False),
            (4, 'session_id', '2026-09-18', False),
            (4, 'provenance_id', 'missing', False),
            (4, 'instrument_id', 'UNKNOWN', True),
            (4, 'price', '100.01', True),
            (4, 'order_id', 'order-sell', True),
            (4, 'quantity', 2, True),
            (4, 'side', 'sell', True),
            (5, 'fill_id', 'fill-sell', True),
            (7, 'market_event_id', 'synthetic-event-011', True),
            (7, 'price', '102.00', True),
            (0, 'tick_value', '10.00', True),
            (0, 'mini_equivalent', '0.0', True),
            (0, 'ftmo_counting_class', 'micro', True),
            (12, 'calendar_id', 'missing', True),
            (1, 'ruleset_sha256', '0' * 64, True),
        ]
        for index, field, value, payload in cases:
            with self.subTest(index=index, field=field):
                trace = copy.deepcopy(self.trace)
                target = trace['events'][index]['payload'] if payload else trace['events'][index]
                target[field] = value
                with self.assertRaises(ValueError):
                    artifacts.validate_trace(trace, self.manifest, self.rules_hash)

    def test_reference_amounts_and_fields_are_strict(self):
        for field, value in [('initial', 50000.0), ('initial', '50000'), ('extra', 'ignored')]:
            with self.subTest(field=field, value=value):
                reference = copy.deepcopy(self.reference)
                reference['cases'][0]['inputs'][field] = value
                with self.assertRaises(ValidationError):
                    artifacts.validate_references(reference, self.manifest)

    def test_reference_ids_and_fee_day_counts(self):
        reference = copy.deepcopy(self.reference)
        reference['cases'][1]['id'] = reference['cases'][0]['id']
        with self.assertRaisesRegex(ValueError, 'Duplicate reference'):
            artifacts.validate_references(reference, self.manifest)
        reference = copy.deepcopy(self.reference)
        case = next(c for c in reference['cases'] if c['kind'] == 'consistency_fees')
        case['inputs']['fees_by_day'].pop()
        with self.assertRaisesRegex(ValueError, 'day counts'):
            artifacts.validate_references(reference, self.manifest)

    def test_fee_vectors_record_user_decision_and_include_open_entry_fees(self):
        case = next(c for c in self.reference['cases'] if c['id'] == 'entry-fees-on-open-positions')
        self.assertEqual(case['decision'], 'human_accepted_lab_convention')
        self.assertEqual(case['inputs']['open_positions_by_day'], [0, 0, 1])
        self.assertEqual(case['expected']['net_days'], ['1200.00', '900.00', '870.00'])
        self.assertFalse(case['expected']['net_satisfied'])

    def test_candidate_three_rejects_incomplete_basis_and_verified_convention_claims(self):
        patches = [
            ('drawdown', 'basis', 'highest_prior_session_closing_balance'),
            ('contract_counting', 'classes', {'standard': '1.0', 'mini': '1.0', 'micro': '1.0'}),
            ('contract_counting', 'classes', {'mini': '1.0', 'micro': '0.1'}),
            ('contract_counting', 'fractional_micro_summation', 'ftmo_verified'),
            ('consistency', 'official_semantics_status', 'ftmo_verified'),
            ('consistency', 'pending_decision', None),
            ('consistency', 'required_reports', ['net_of_fees_consistency_share']),
            ('consistency', 'allow_silent_substitution', True),
        ]
        for section, key, value in patches:
            with self.subTest(section=section, key=key):
                manifest = copy.deepcopy(self.manifest)
                manifest[section][key] = value
                with self.assertRaises(ValidationError):
                    artifacts.validate_schema(manifest, 'rules/schema.json')

    def test_instrument_requires_known_counting_class_matching_weight(self):
        for value in (None, 'unknown', 'standard'):
            with self.subTest(value=value):
                trace = copy.deepcopy(self.trace)
                payload = trace['events'][0]['payload']
                if value is None:
                    del payload['ftmo_counting_class']
                else:
                    payload['ftmo_counting_class'] = value
                    payload['mini_equivalent'] = '0.1'
                with self.assertRaises((ValidationError, ValueError)):
                    artifacts.validate_trace(trace, self.manifest, self.rules_hash)

    def test_remediation_boundary_vectors_are_explicit(self):
        cases = {c['id']: c for c in self.reference['cases']}
        self.assertEqual(cases['no-prior-close']['inputs']['prior_closes'], [])
        self.assertEqual(cases['no-prior-close']['expected']['session_start_floors'], ['48000.00'])
        self.assertEqual(cases['losing-first-close']['expected']['session_start_floors'],
                         ['48000.00', '48000.00'])
        self.assertEqual(cases['all-closes-below-initial']['expected']['session_start_floors'],
                         ['48000.00', '48000.00', '48000.00'])
        self.assertEqual(cases['official-four-plus-ten']['inputs']['standard_contracts'], 4)
        self.assertEqual(cases['official-four-plus-ten']['inputs']['mini_contracts'], 0)
        self.assertEqual(cases['one-micro']['expected']['mini_equivalent'], '0.1')
        self.assertEqual(cases['one-micro']['decision'], 'lab_convention_pending_ftmo_confirmation')

    def test_dual_consistency_vectors_preserve_distinct_results_and_labels(self):
        cases = {c['id']: c for c in self.reference['cases']}
        expected = cases['fees-change-consistency']['expected']
        self.assertEqual(expected['gross_consistency_share']['share'], '2/5')
        self.assertEqual(expected['net_of_fees_consistency_share']['share'], '40/99')
        self.assertTrue(expected['gross_satisfied'])
        self.assertFalse(expected['net_satisfied'])
        self.assertEqual(expected['net_of_fees_label'], 'lab_convention_pending_verification')
        for key in ('gross_consistency_share', 'net_of_fees_consistency_share', 'net_of_fees_label'):
            reference = copy.deepcopy(self.reference)
            case = next(c for c in reference['cases'] if c['id'] == 'fees-change-consistency')
            del case['expected'][key]
            with self.subTest(missing=key), self.assertRaises(ValidationError):
                artifacts.validate_references(reference, self.manifest)
        expected = cases['fees-change-best-day']['expected']
        self.assertEqual(expected['gross_consistency_share']['best_day'], '1200.00')
        self.assertEqual(expected['net_of_fees_consistency_share']['best_day'], '1100.00')
        expected = cases['fees-make-net-total-zero']['expected']
        self.assertIsNotNone(expected['gross_consistency_share']['share'])
        self.assertIsNone(expected['net_of_fees_consistency_share']['share'])
        self.assertEqual(expected['net_of_fees_consistency_share']['reason'], 'nonpositive_total_profit')

    def test_session_vectors_match_zoneinfo_across_both_dst_changes(self):
        zone = ZoneInfo('America/New_York')
        windows = [c for c in self.reference['cases'] if c['kind'] == 'session_window']
        self.assertEqual(len(windows), 4)
        for case in windows:
            with self.subTest(case=case['id']):
                closing_day = date.fromisoformat(case['inputs']['session_id'])
                start = datetime.combine(closing_day - timedelta(days=1), time(18), zone)
                close = datetime.combine(closing_day, time(16, 10), zone)
                self.assertEqual(start, datetime.fromisoformat(case['expected']['start_utc']))
                self.assertEqual(close, datetime.fromisoformat(case['expected']['close_utc']))
                self.assertLess(closing_day.weekday(), 5)

    def test_parsers_reject_duplicate_keys_nonfinite_numbers_and_yaml_tags(self):
        examples = [('.json', '{"a":1,"a":2}'), ('.json', '{"a":NaN}'),
                    ('.yaml', 'a: 1\na: 2\n'),
                    ('.yaml', 'a: !!python/object:builtins.object {}')]
        with tempfile.TemporaryDirectory() as folder:
            for suffix, text in examples:
                with self.subTest(text=text):
                    path = Path(folder) / ('invalid' + suffix)
                    path.write_text(text)
                    with self.assertRaises((ValueError, yaml.YAMLError)):
                        artifacts.read_artifact(path)


if __name__ == '__main__':
    unittest.main()
