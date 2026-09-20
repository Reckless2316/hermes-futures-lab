"""Every accepted P0 reference vector invokes executable P1 behavior."""

import json
import unittest
from datetime import datetime
from decimal import Decimal as D
from pathlib import Path
from tempfile import TemporaryDirectory

from futures_lab.data.calendar import Calendar
from futures_lab.domain.values import DataError
from futures_lab.engine import evaluate_document
from futures_lab.rules.financial import Drawdown, consistency, exposure, target_met
from futures_lab.rules.manifest import load_rules

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "rules/ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.3.yaml"


class FinancialRuleTests(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules(RULES)
        self.trace = json.loads((ROOT / "tests/fixtures/round_trip.json").read_text())
        self.calendar = Calendar.parse(self.trace["calendar"])

    def test_all_51_p0_reference_vectors(self):
        cases = json.loads(
            (ROOT / "tests/fixtures/growth_50k_reference.json").read_text()
        )["cases"]
        self.assertEqual(len(cases), 51)
        visited = set()
        for case in cases:
            with self.subTest(vector=case["id"]):
                i, expected, kind = case["inputs"], case["expected"], case["kind"]
                actual = self.vector(kind, i)
                self.assertEqual({k: actual[k] for k in expected}, expected)
                visited.add(case["id"])
        self.assertEqual(len(visited), 51)

    def vector(self, kind, i):
        r = self.rules
        floor = Drawdown.initial_state(r.initial, r.drawdown)
        if kind == "floor_sequence":
            floor = Drawdown.initial_state(D(i["initial"]), r.drawdown)
            values = [format(floor.floor, ".2f")]
            for close in i["prior_closes"]:
                floor = floor.close(D(close)).start()
                values.append(format(floor.floor, ".2f"))
            return {"session_start_floors": values}
        if kind == "equity_boundary":
            floor = Drawdown(r.initial, r.drawdown, r.initial, D(i["floor"]))
            return {"breached": floor.observe(D(i["equity"])).breached}
        if kind == "fee_equity":
            equity = D(i["cash_before_fee"]) - D(i["fee"]) + D(i["unrealized"])
            floor = Drawdown(r.initial, r.drawdown, r.initial, D(i["floor"]))
            return {
                "equity": format(equity, ".2f"),
                "breached": floor.observe(equity).breached,
            }
        if kind == "floor_timing":
            floor = Drawdown(r.initial, r.drawdown, r.initial, D(i["active_floor"]))
            during = floor.observe(D(i["intraday_balance"])).floor
            floor = floor.close(D(i["closing_balance"]))
            return {
                "floor_during_session": format(during, ".2f"),
                "floor_at_close": format(floor.floor, ".2f"),
                "floor_next_start": format(floor.start().floor, ".2f"),
            }
        if kind == "breach_history":
            floor = Drawdown(r.initial, r.drawdown, r.initial, D(i["floor"]))
            for value in i["equities"]:
                floor = floor.observe(D(value))
            return {"breached": floor.breached}
        if kind == "target":
            return {
                "target_condition_met": target_met(
                    D(i["balance"]),
                    r.initial,
                    r.target,
                    i["open_positions"],
                    i["after_session_close"],
                )
            }
        if kind == "consistency":
            return {
                **consistency(tuple(map(D, i["closed_days"])), r.consistency_limit),
                "breached": False,
            }
        if kind == "consistency_fees":
            net = tuple(D(g) - D(f) for g, f in zip(i["gross_days"], i["fees_by_day"]))
            gross_view = consistency(
                tuple(map(D, i["gross_days"])), r.consistency_limit
            )
            net_view = consistency(net, r.consistency_limit)
            return {
                "gross_satisfied": gross_view["satisfied"],
                "net_satisfied": net_view["satisfied"],
                "net_days": [format(v, ".2f") for v in net],
                "gross_consistency_share": {
                    k: v for k, v in gross_view.items() if k != "satisfied"
                },
                "net_of_fees_consistency_share": {
                    k: v for k, v in net_view.items() if k != "satisfied"
                },
                "net_of_fees_label": "lab_convention_pending_verification",
            }
        if kind == "daily_loss":
            return {
                "daily_loss_limit": None,
                "drawdown_breached": Drawdown(
                    r.initial, r.drawdown, r.initial, D(i["floor"])
                )
                .observe(D(i["equity"]))
                .breached,
            }
        if kind in {"exposure", "signed_exposure"}:
            positions = (
                tuple(
                    (qty, r.weight("mini"))
                    for qty in i["mini_positions_by_contract"].values()
                )
                if kind == "signed_exposure"
                else tuple(
                    (i[name + "_contracts"], r.weight(name))
                    for name in ("standard", "mini", "micro")
                )
            )
            return {
                **exposure(positions, r.exposure_limit),
                "official_semantics_status": "unresolved_pending_ftmo_confirmation",
            }
        if kind == "session_window":
            from datetime import date, time, timedelta
            from zoneinfo import ZoneInfo

            day, zone = date.fromisoformat(i["session_id"]), ZoneInfo(i["timezone"])
            start = datetime.combine(day - timedelta(days=1), time(18), zone)
            close = datetime.combine(day, time(16, 10), zone)
            # Calendar validates the supplied UTC window against the actual zone rules.
            from datetime import timezone

            row = {
                "session_id": i["session_id"],
                "start_utc": start.astimezone(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "close_utc": close.astimezone(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            }
            calendar = Calendar.parse(
                {"id": "dst", "timezone": i["timezone"], "sessions": [row]}
            )
            s = calendar.sessions[0]
            return {
                "start_utc": s.start.isoformat().replace("+00:00", "Z"),
                "close_utc": s.close.isoformat().replace("+00:00", "Z"),
            }
        if kind == "session_boundary":
            try:
                value = self.calendar.locate(
                    datetime.fromisoformat(i["timestamp_utc"]), i["event_type"]
                ).id
            except DataError:
                value = "quarantine"
            return {"session_or_disposition": value}
        if kind == "data_quality":
            d = json.loads(json.dumps(self.trace))
            if i["condition"] == "missing_instrument_spec":
                del d["events"][0]
            elif i["condition"] == "missing_position_mark":
                d["events"][5]["timestamp_utc"] = "2026-09-17T14:00:02Z"
            elif i["condition"] == "missing_calendar":
                d["calendar"]["sessions"] = []
            elif i["condition"] == "idempotency_conflict":
                bad = json.loads(json.dumps(d["events"][0]))
                bad["payload"]["symbol"] = "conflict"
                d["events"].append(bad)
            else:
                self.fail("Unhandled data-quality vector")
            return evaluate_document(d, r, input_sha256="0" * 64, code_version="test")[
                "report"
            ]
        self.fail("Unhandled vector kind: " + kind)

    def test_rules_reject_changed_and_historical_bytes(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "rules.yaml"
            path.write_bytes(RULES.read_bytes() + b"\n")
            with self.assertRaisesRegex(DataError, "unapproved_rules_bytes"):
                load_rules(path)
        for name in (
            "ftmo_futures_growth_evaluation_50k_2026-09-17.yaml",
            "ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.2.yaml",
        ):
            with self.assertRaisesRegex(DataError, "unapproved_rules_bytes"):
                load_rules(ROOT / "rules" / name)

    def test_drawdown_monotonic_over_pathological_sequences(self):
        import itertools

        for closes in itertools.product(
            map(D, ["48001.00", "49000.00", "50000.00", "51000.00", "52500.00"]),
            repeat=4,
        ):
            state = Drawdown.initial_state(self.rules.initial, self.rules.drawdown)
            previous = state.floor
            for close in closes:
                state = state.close(close).start()
                self.assertGreaterEqual(state.floor, previous)
                self.assertLessEqual(state.floor, self.rules.initial)
                previous = state.floor

    def test_target_one_cent_above_and_counting_have_one_configuration(self):
        self.assertTrue(
            target_met(D("53000.01"), self.rules.initial, self.rules.target, 0, True)
        )
        self.assertFalse(
            target_met(D("53000.01"), self.rules.initial, self.rules.target, 1, True)
        )
        self.assertEqual(
            exposure(((5, self.rules.weight("standard")),), self.rules.exposure_limit),
            {"mini_equivalent": "5.0", "within_cap": True},
        )
        self.assertEqual(
            exposure(((50, self.rules.weight("micro")),), self.rules.exposure_limit),
            {"mini_equivalent": "5.0", "within_cap": True},
        )
