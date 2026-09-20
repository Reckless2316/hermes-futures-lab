"""End-to-end multi-session assessments, distinct fee views and multi-instrument risk."""

import copy
import unittest
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal as D
from zoneinfo import ZoneInfo

from tests.test_engine import evaluate, make_engine, trace


def multi_day(gross_days, fee_days):
    d = trace()
    base = d["events"][0]
    rules = d["events"][1]
    d["events"] = []
    d["calendar"]["sessions"] = []
    days = ["2026-09-17", "2026-09-18", "2026-09-21", "2026-09-22"][: len(gross_days)]
    for day, gross, fee in zip(days, gross_days, fee_days):
        local = date.fromisoformat(day)
        zone = ZoneInfo("America/New_York")
        start = datetime.combine(local - timedelta(days=1), time(18), zone)
        close = datetime.combine(local, time(16, 10), zone)
        d["calendar"]["sessions"].append(
            {
                "session_id": day,
                "start_utc": start.astimezone(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "close_utc": close.astimezone(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            }
        )

        def add(kind, payload, stamp):
            n = len(d["events"]) + 1
            event = {
                **base,
                "event_id": f"e-{n}",
                "source_event_id": f"row-{n}",
                "sequence": n,
                "session_id": day,
                "timestamp_utc": day + "T" + stamp + "Z",
                "event_type": kind,
                "payload": payload,
            }
            d["events"].append(event)
            return event["event_id"]

        if not d["events"]:
            add("InstrumentSpec", copy.deepcopy(base["payload"]), "13:00:00")
            add("RulesetSelected", copy.deepcopy(rules["payload"]), "13:00:00")
        for side, stamp, price in [
            ("buy", "14:00:01", "100.00"),
            ("sell", "14:01:01", format(D("100") + D(gross) / D("50"), ".2f")),
        ]:
            order = day + side
            ref = add(
                "OrderIntent",
                {
                    "order_id": order,
                    "instrument_id": base["payload"]["instrument_id"],
                    "side": side,
                    "quantity": 1,
                    "order_type": "market",
                },
                stamp,
            )
            add("OrderAccepted", {"order_id": order, "intent_event_id": ref}, stamp)
            fill_id = order + "-fill"
            add(
                "Fill",
                {
                    "order_id": order,
                    "fill_id": fill_id,
                    "instrument_id": base["payload"]["instrument_id"],
                    "side": side,
                    "quantity": 1,
                    "price": price,
                },
                stamp,
            )
            if side == "sell":
                add(
                    "Commission",
                    {"fill_id": fill_id, "amount": fee, "currency": "USD"},
                    stamp,
                )
        add("SessionClose", {"calendar_id": d["calendar"]["id"]}, "20:10:00")
    return d


class AssessmentTests(unittest.TestCase):
    def test_candidate_lab_estimate_with_exact_target_and_consistency(self):
        d = multi_day(["1200.00", "900.00", "900.00"], ["0.00"] * 3)
        result = evaluate(d)["report"]
        self.assertEqual(result["balance"], "53000.00")
        self.assertEqual(result["state"], "eligible_estimate")
        self.assertEqual(result["ruleset_review_status"], "pending")
        self.assertEqual(result["evaluation_mode"], "candidate_3_lab_estimate")
        self.assertFalse(result["official_account_certification"])
        self.assertEqual(result["gross_consistency_share"]["share"], "2/5")
        self.assertEqual(result["data_quality_reasons"], [])

    def test_target_met_gross_pass_net_fail_explains_basis_divergence(self):
        # Smaller days bear fees: the best day stays 1300 while total falls to 3160.
        result = evaluate(
            multi_day(["1300.00", "1000.00", "1000.00"], ["0.00", "70.00", "70.00"])
        )["report"]
        self.assertEqual(result["balance"], "53160.00")
        self.assertTrue(result["target_condition_met"])
        self.assertTrue(result["gross_consistency_share"]["satisfied"])
        self.assertFalse(result["net_of_fees_consistency_share"]["satisfied"])
        self.assertEqual(result["gross_consistency_share"]["share"], "13/33")
        self.assertEqual(result["net_of_fees_consistency_share"]["share"], "65/158")
        self.assertEqual(result["state"], "not_yet_eligible")
        self.assertEqual(
            result["data_quality_reasons"], ["consistency_basis_divergence"]
        )
        self.assertFalse(result["drawdown_breached"])
        self.assertEqual(result["breach_evidence_event_ids"], [])
        self.assertEqual(result["quarantine"], [])
        self.assertEqual(result["valuation_gaps"], [])
        self.assertFalse(result["official_account_certification"])
        self.assertEqual(
            result["net_of_fees_label"], "lab_convention_pending_verification"
        )

    def test_target_met_gross_fail_net_pass_explains_basis_divergence(self):
        # Fees on the best day reduce its share: 1400/3400 becomes 1200/3200.
        result = evaluate(
            multi_day(["1400.00", "1000.00", "1000.00"], ["200.00", "0.00", "0.00"])
        )["report"]
        self.assertEqual(result["balance"], "53200.00")
        self.assertTrue(result["target_condition_met"])
        self.assertFalse(result["gross_consistency_share"]["satisfied"])
        self.assertTrue(result["net_of_fees_consistency_share"]["satisfied"])
        self.assertEqual(result["gross_consistency_share"]["share"], "7/17")
        self.assertEqual(result["net_of_fees_consistency_share"]["share"], "3/8")
        self.assertEqual(result["state"], "eligible_estimate")
        self.assertEqual(
            result["data_quality_reasons"], ["consistency_basis_divergence"]
        )
        self.assertFalse(result["drawdown_breached"])
        self.assertEqual(result["breach_evidence_event_ids"], [])
        self.assertEqual(result["quarantine"], [])
        self.assertEqual(result["valuation_gaps"], [])
        self.assertFalse(result["official_account_certification"])
        self.assertEqual(
            result["net_of_fees_label"], "lab_convention_pending_verification"
        )

    def test_fees_change_share_without_silent_gross_substitution(self):
        d = multi_day(["1200.00", "900.00", "900.00"], ["0.00", "0.00", "30.00"])
        result = evaluate(d)["report"]
        self.assertEqual(result["gross_consistency_share"]["share"], "2/5")
        self.assertEqual(result["net_of_fees_consistency_share"]["share"], "40/99")
        self.assertEqual(
            result["net_of_fees_label"], "lab_convention_pending_verification"
        )
        self.assertEqual(result["state"], "not_yet_eligible")
        self.assertFalse(result["drawdown_breached"])

    def test_consistency_alone_defers_eligibility(self):
        result = evaluate(multi_day(["2000.00", "1000.00"], ["0.00"] * 2))["report"]
        self.assertTrue(result["target_condition_met"])
        self.assertEqual(result["state"], "not_yet_eligible")
        self.assertFalse(result["drawdown_breached"])

    def test_entry_fee_on_open_position_uses_posting_session(self):
        d = multi_day(["1200.00", "900.00", "900.00"], ["0.00"] * 3)
        close = d["events"].pop()
        last = d["events"][-1]
        seq = last["sequence"]

        def add(kind, payload):
            nonlocal seq
            seq += 1
            d["events"].append(
                {
                    **last,
                    "event_id": f"late-{seq}",
                    "source_event_id": f"late-{seq}",
                    "sequence": seq,
                    "event_type": kind,
                    "timestamp_utc": "2026-09-21T19:00:00Z",
                    "payload": payload,
                }
            )
            return f"late-{seq}"

        ref = add(
            "OrderIntent",
            {
                "order_id": "open",
                "instrument_id": "LAB-MINI-202609",
                "side": "buy",
                "quantity": 1,
                "order_type": "market",
            },
        )
        add("OrderAccepted", {"order_id": "open", "intent_event_id": ref})
        add(
            "Fill",
            {
                "order_id": "open",
                "fill_id": "open-fill",
                "instrument_id": "LAB-MINI-202609",
                "side": "buy",
                "quantity": 1,
                "price": "100.00",
            },
        )
        add(
            "Commission", {"fill_id": "open-fill", "amount": "30.00", "currency": "USD"}
        )
        close.update(
            sequence=seq + 1, event_id="final-close", source_event_id="final-close"
        )
        d["events"].append(close)
        result = evaluate(d)["report"]
        self.assertEqual(result["balance"], "52970.00")
        self.assertEqual(result["gross_consistency_share"]["share"], "2/5")
        self.assertEqual(result["net_of_fees_consistency_share"]["share"], "40/99")
        self.assertFalse(result["target_condition_met"])
        self.assertEqual(result["open_positions"], 1)
        self.assertEqual(
            result["state"], "data_unavailable"
        )  # No close-time mark supplied.

    def test_multiple_contracts_opposite_positions_never_offset_exposure(self):
        d = trace()
        d["provenance"]["instrument_spec_ids"].append("LAB-OTHER")
        engine = make_engine(d)
        seq = 0

        def add(template):
            nonlocal seq
            seq += 1
            e = copy.deepcopy(template)
            e.update(
                event_id=f"m-{seq}",
                source_event_id=f"m-{seq}",
                sequence=seq,
                timestamp_utc="2026-09-17T14:00:01Z",
            )
            self.assertEqual(engine.append(e)["disposition"], "accepted")
            return e["event_id"]

        add(d["events"][0])
        other = copy.deepcopy(d["events"][0])
        other["payload"].update(
            instrument_id="LAB-OTHER", ftmo_counting_class="standard"
        )
        add(other)
        add(d["events"][1])
        for ident, side, qty in [
            ("LAB-MINI-202609", "buy", 3),
            ("LAB-OTHER", "sell", 2),
        ]:
            intent = copy.deepcopy(d["events"][2])
            intent["payload"].update(
                order_id=ident, instrument_id=ident, side=side, quantity=qty
            )
            ref = add(intent)
            accepted = copy.deepcopy(d["events"][3])
            accepted["payload"].update(order_id=ident, intent_event_id=ref)
            add(accepted)
            fill = copy.deepcopy(d["events"][4])
            fill["payload"].update(
                order_id=ident,
                instrument_id=ident,
                fill_id=ident,
                side=side,
                quantity=qty,
            )
            add(fill)
        report = engine.report()
        self.assertEqual(report["exposure"]["mini_equivalent"], "5.0")
        self.assertEqual(report["open_positions"], 2)
        self.assertEqual(report["equity"], "50000.00")
        self.assertEqual(report["data_quality_reasons"], [])

    def test_first_losing_close_keeps_initial_floor_then_winning_close_ratchets(self):
        d = multi_day(["-1000.00", "1500.00"], ["0.00"] * 2)
        result = evaluate(d)
        reports = [r for r in result["checkpoints"] if r["after_session_close"]]
        self.assertEqual([r["floor"] for r in reports], ["48000.00", "48000.00"])
        self.assertEqual(result["report"]["balance"], "50500.00")
