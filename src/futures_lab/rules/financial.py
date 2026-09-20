"""Pure, explicit formulas. Manifest expression text is never interpreted."""

from dataclasses import dataclass, replace
from decimal import Decimal
from fractions import Fraction

from futures_lab.domain.values import exact, money_text


@dataclass(frozen=True)
class Drawdown:
    initial: Decimal
    amount: Decimal
    highest_close: Decimal
    floor: Decimal
    breached: bool = False

    @classmethod
    def initial_state(cls, initial: Decimal, amount: Decimal) -> "Drawdown":
        with exact():
            return cls(initial, amount, initial, initial - amount)

    def close(self, balance: Decimal) -> "Drawdown":
        return replace(
            self, highest_close=max(self.initial, self.highest_close, balance)
        )

    def start(self) -> "Drawdown":
        with exact():
            basis = max(self.initial, self.highest_close)
            return replace(self, floor=min(self.initial, basis - self.amount))

    def observe(self, equity: Decimal | None) -> "Drawdown":
        return replace(
            self,
            breached=self.breached or (equity is not None and equity <= self.floor),
        )


def consistency(days: tuple[Decimal, ...], limit: Decimal) -> dict:
    with exact():
        total = sum(days, Decimal("0.00"))
        best = max((Decimal("0.00"), *days))
        ratio = Fraction(best) / Fraction(total) if total > 0 else None
        return {
            "best_day": money_text(best),
            "total": money_text(total),
            "share": None
            if ratio is None
            else f"{ratio.numerator}/{ratio.denominator}",
            "reason": "nonpositive_total_profit" if ratio is None else None,
            "satisfied": total > 0 and best <= total * limit,
        }


def exposure(positions: tuple[tuple[int, Decimal], ...], limit: Decimal) -> dict:
    with exact():
        value = sum((abs(qty) * weight for qty, weight in positions), Decimal("0.0"))
        return {"mini_equivalent": format(value, ".1f"), "within_cap": value <= limit}


def target_met(
    balance: Decimal,
    initial: Decimal,
    target: Decimal,
    open_positions: int,
    after_session_close: bool,
) -> bool:
    with exact():
        return (
            after_session_close and open_positions == 0 and balance >= initial + target
        )
