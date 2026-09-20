"""Append-only normalized event journal and exact FIFO lot accounting."""

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256

from .events import Event, Instrument
from .values import cents, exact, require


class Journal:
    def __init__(self):
        self._events: tuple[Event, ...] = ()
        self._keys: dict[tuple[str, str, str], Event] = {}
        self._ids: set[str] = set()
        self._digest = sha256(b"[")

    @property
    def events(self) -> tuple[Event, ...]:
        return self._events

    @property
    def sha256(self) -> str:
        digest = self._digest.copy()
        digest.update(b"]")
        return digest.hexdigest()

    def check(self, event: Event) -> bool:
        previous = self._keys.get(event.import_key)
        if previous is not None:
            require(previous.wire == event.wire, "idempotency_conflict")
            return False
        require(event.event_id not in self._ids, "duplicate_event_id")
        if self._events:
            last = self._events[-1]
            require(event.account_id == last.account_id, "account_mismatch")
            require(event.sequence > last.sequence, "out_of_order_sequence")
            require(event.time >= last.time, "out_of_order_timestamp")
        return True

    def append(self, event: Event) -> bool:
        if not self.check(event):
            return False
        if self._events:
            self._digest.update(b",")
        self._digest.update(event.wire.encode())
        self._events += (event,)
        self._keys[event.import_key] = event
        self._ids.add(event.event_id)
        return True


@dataclass(frozen=True)
class Lot:
    quantity: int  # Signed, nonzero.
    price: Decimal
    fill_id: str


@dataclass(frozen=True)
class Position:
    lots: tuple[Lot, ...] = ()

    @property
    def quantity(self) -> int:
        return sum(lot.quantity for lot in self.lots)

    def fill(
        self, quantity: int, price: Decimal, spec: Instrument, fill_id: str
    ) -> tuple["Position", Decimal]:
        require(type(quantity) is int and quantity != 0, "invalid_fill_quantity")
        spec.check_price(price)
        lots = list(self.lots)
        remaining, realized = quantity, Decimal("0.00")
        with exact():
            while remaining and lots and (remaining > 0) != (lots[0].quantity > 0):
                lot = lots.pop(0)
                sign = 1 if lot.quantity > 0 else -1
                closed = min(abs(remaining), abs(lot.quantity))
                realized += (
                    ((price - lot.price) / spec.tick_size)
                    * spec.tick_value
                    * closed
                    * sign
                )
                remaining += closed * sign
                left = lot.quantity - closed * sign
                if left:
                    lots.insert(0, Lot(left, lot.price, lot.fill_id))
            if remaining:
                lots.append(Lot(remaining, price, fill_id))
            return Position(tuple(lots)), cents(realized)

    def unrealized(self, mark: Decimal, spec: Instrument) -> Decimal:
        spec.check_price(mark)
        with exact():
            return cents(
                sum(
                    (
                        (mark - lot.price)
                        / spec.tick_size
                        * spec.tick_value
                        * lot.quantity
                        for lot in self.lots
                    ),
                    Decimal("0.00"),
                )
            )
