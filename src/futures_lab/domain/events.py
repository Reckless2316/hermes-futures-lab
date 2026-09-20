"""Normalized, immutable events. Unknown fields/types are rejected."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import json

from .values import DataError, decimal, fields, integer, require, text, timestamp, exact

PAYLOADS = {
    "InstrumentSpec": (
        {
            "instrument_id",
            "symbol",
            "venue",
            "currency",
            "tick_size",
            "tick_value",
            "multiplier",
            "ftmo_counting_class",
            "mini_equivalent",
            "expiry",
            "calendar_id",
            "roll_policy",
        },
        set(),
    ),
    "RulesetSelected": ({"ruleset_id", "rules_version", "ruleset_sha256"}, set()),
    "OrderIntent": (
        {"order_id", "instrument_id", "side", "quantity", "order_type"},
        {"limit_price", "stop_price"},
    ),
    "OrderAccepted": ({"order_id", "intent_event_id"}, set()),
    "OrderRejected": ({"order_id", "intent_event_id", "reason_code"}, set()),
    "Fill": (
        {"fill_id", "order_id", "instrument_id", "side", "quantity", "price"},
        set(),
    ),
    "Commission": ({"fill_id", "amount", "currency"}, set()),
    "PositionMark": ({"instrument_id", "price", "market_event_id"}, set()),
    "SessionClose": ({"calendar_id"}, set()),
    "JournalNote": ({"referenced_event_ids", "text"}, set()),
}
BASE = {
    "schema_version",
    "event_id",
    "event_type",
    "account_id",
    "source",
    "source_event_id",
    "timestamp_utc",
    "session_id",
    "sequence",
    "provenance_id",
    "payload",
}


def canonical(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


@dataclass(frozen=True)
class Event:
    """Own canonical bytes instead of retaining mutable caller dictionaries."""

    wire: str
    event_id: str
    kind: str
    account_id: str
    source: str
    source_event_id: str
    time: datetime
    session_id: str
    sequence: int
    provenance_id: str

    @property
    def payload(self) -> dict:
        return json.loads(self.wire)["payload"]

    @property
    def import_key(self) -> tuple[str, str, str]:
        return self.account_id, self.source, self.source_event_id

    @classmethod
    def parse(cls, raw: object) -> "Event":
        d = fields(raw, BASE)
        require(
            type(d["schema_version"]) is int and d["schema_version"] == 1,
            "unknown_schema_version",
        )
        for key in BASE - {"schema_version", "sequence", "payload", "timestamp_utc"}:
            text(d[key])
        integer(d["sequence"], minimum=1)
        stamp = timestamp(d["timestamp_utc"])
        try:
            require(
                date.fromisoformat(d["session_id"]).isoformat() == d["session_id"],
                "invalid_session_id",
            )
        except ValueError as error:
            raise DataError("invalid_session_id") from error
        kind = d["event_type"]
        require(kind != "Correction", "correction_not_implemented")
        if kind == "MarketEvent":
            p = d["payload"]
            require(type(p) is dict, "expected_object")
            required = {"instrument_id", "kind"}
            shape = {
                "trade": {"price", "volume"},
                "quote": {"bid", "ask"},
                "bar": {"open", "high", "low", "close", "volume", "interval_seconds"},
            }
            require(
                isinstance(p.get("kind"), str) and p["kind"] in shape,
                "unknown_market_kind",
            )
            fields(p, required | shape[p["kind"]])
        else:
            require(kind in PAYLOADS, "unknown_event_type")
            p = fields(d["payload"], *PAYLOADS[kind])
        for key, value in p.items():
            if key in {
                "price",
                "limit_price",
                "stop_price",
                "tick_size",
                "tick_value",
                "multiplier",
                "mini_equivalent",
                "bid",
                "ask",
                "open",
                "high",
                "low",
                "close",
            }:
                decimal(
                    value,
                    positive=key
                    in {"tick_size", "tick_value", "multiplier", "mini_equivalent"},
                )
            elif key == "amount":
                require(decimal(value, money=True) >= 0, "negative_commission")
            elif key in {"quantity", "interval_seconds"}:
                integer(value, minimum=1)
            elif key == "volume":
                integer(value)
            elif key == "referenced_event_ids":
                require(type(value) is list and len(value) <= 100, "invalid_references")
                for ref in value:
                    text(ref)
            elif key == "text":
                require(isinstance(value, str) and len(value) <= 4096, "invalid_note")
            else:
                text(value)
        if "side" in p:
            require(p["side"] in {"buy", "sell"}, "invalid_side")
        if "currency" in p:
            require(p["currency"] == "USD", "unsupported_currency")
        if kind == "OrderIntent":
            require(
                p["order_type"] in {"market", "limit", "stop"}, "unsupported_order_type"
            )
            prices = {
                "market": set(),
                "limit": {"limit_price"},
                "stop": {"stop_price"},
            }[p["order_type"]]
            require(
                set(p) & {"limit_price", "stop_price"} == prices, "invalid_order_prices"
            )
        if kind == "InstrumentSpec":
            require(
                p["ftmo_counting_class"] in {"standard", "mini", "micro"},
                "unknown_counting_class",
            )
            try:
                require(
                    date.fromisoformat(p["expiry"]).isoformat() == p["expiry"],
                    "invalid_expiry",
                )
            except ValueError as error:
                raise DataError("invalid_expiry") from error
            with exact():
                require(
                    decimal(p["tick_size"]) * decimal(p["multiplier"])
                    == decimal(p["tick_value"]),
                    "inconsistent_tick_specification",
                )
        return cls(
            canonical(d),
            d["event_id"],
            kind,
            d["account_id"],
            d["source"],
            d["source_event_id"],
            stamp,
            d["session_id"],
            d["sequence"],
            d["provenance_id"],
        )


@dataclass(frozen=True)
class Instrument:
    instrument_id: str
    tick_size: Decimal
    tick_value: Decimal
    multiplier: Decimal
    counting_class: str
    calendar_id: str

    @classmethod
    def from_event(cls, event: Event) -> "Instrument":
        p = event.payload
        return cls(
            p["instrument_id"],
            decimal(p["tick_size"]),
            decimal(p["tick_value"]),
            decimal(p["multiplier"]),
            p["ftmo_counting_class"],
            p["calendar_id"],
        )

    def check_price(self, price: Decimal) -> None:
        with exact():
            require(price % self.tick_size == 0, "off_tick_price")
