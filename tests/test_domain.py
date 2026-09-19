"""Domain tests exercise accounting independently from the rule engine."""
import copy
import json
import unittest
from decimal import Decimal, localcontext
from pathlib import Path

from futures_lab.domain.events import Event, Instrument
from futures_lab.domain.ledger import Journal, Position
from futures_lab.domain.values import DataError, decimal, money_text

ROOT = Path(__file__).resolve().parents[1]


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.trace = json.loads((ROOT / 'tests/fixtures/round_trip.json').read_text())
        self.spec = Instrument.from_event(Event.parse(self.trace['events'][0]))

    def test_wire_values_reject_floats_nonfinite_and_rounding(self):
        for value in [1.1, True, 'NaN', 'Infinity', '1e2', '01.00', '1.00\n', '0.001']:
            with self.subTest(value=value), self.assertRaises(DataError):
                decimal(value, money=True)
        self.assertEqual(money_text(decimal('-12.50', money=True)), '-12.50')

    def test_fifo_partial_exit_then_reverse_short(self):
        p, _ = Position().fill(2, Decimal('100.00'), self.spec, 'a')
        p, _ = p.fill(1, Decimal('101.00'), self.spec, 'b')
        p, pnl = p.fill(-1, Decimal('102.00'), self.spec, 'c')
        self.assertEqual(pnl, Decimal('100.00'))
        self.assertEqual(p.quantity, 2)
        p, pnl = p.fill(-3, Decimal('103.00'), self.spec, 'd')
        self.assertEqual(pnl, Decimal('250.00'))
        self.assertEqual(p.quantity, -1)
        self.assertEqual(p.unrealized(Decimal('102.00'), self.spec), Decimal('50.00'))
        p, pnl = p.fill(1, Decimal('101.00'), self.spec, 'e')
        self.assertEqual(pnl, Decimal('100.00'))
        self.assertEqual(p.lots, ())

    def test_off_tick_and_fractional_cent_fail(self):
        with self.assertRaises(DataError):
            Position().fill(1, Decimal('100.01'), self.spec, 'bad')
        from futures_lab.domain.values import cents
        with self.assertRaises(DataError):
            cents(Decimal('0.001'))

    def test_context_cannot_round_financial_results(self):
        with localcontext() as context:
            context.prec = 3
            p, _ = Position().fill(100, Decimal('123456.25'), self.spec, 'a')
            _, pnl = p.fill(-100, Decimal('123457.50'), self.spec, 'b')
            self.assertEqual(pnl, Decimal('6250.00'))

    def test_event_owns_bytes_and_payload_copy(self):
        raw = copy.deepcopy(self.trace['events'][0])
        event = Event.parse(raw)
        raw['payload']['symbol'] = 'mutated'
        returned = event.payload
        returned['symbol'] = 'also-mutated'
        self.assertEqual(event.payload['symbol'], 'LAB-MINI')

    def test_idempotency_ordering_and_conflict(self):
        journal = Journal()
        a, b = [Event.parse(e) for e in self.trace['events'][:2]]
        self.assertTrue(journal.append(a))
        self.assertTrue(journal.append(b))
        self.assertFalse(journal.append(a))
        self.assertEqual(journal.events, (a, b))
        changed = copy.deepcopy(self.trace['events'][0]); changed['payload']['symbol'] = 'different'
        with self.assertRaisesRegex(DataError, 'idempotency_conflict'):
            journal.append(Event.parse(changed))
        bad = copy.deepcopy(self.trace['events'][2]); bad['sequence'] = 2
        with self.assertRaisesRegex(DataError, 'out_of_order_sequence'):
            journal.append(Event.parse(bad))

    def test_boolean_quantity_unknown_fields_and_correction_rejected(self):
        for key, value in [('quantity', True), ('extra', 'unexpected')]:
            raw = copy.deepcopy(self.trace['events'][4]); raw['payload'][key] = value
            with self.assertRaises(DataError):
                Event.parse(raw)
        raw = copy.deepcopy(self.trace['events'][4]); raw['event_type'] = 'Correction'
        with self.assertRaisesRegex(DataError, 'correction_not_implemented'):
            Event.parse(raw)
