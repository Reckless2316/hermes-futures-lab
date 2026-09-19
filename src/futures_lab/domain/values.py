"""Strict wire values and arithmetic independent of the caller's Decimal context."""

import re
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Context, Decimal, Inexact, localcontext


class DataError(ValueError):
    """An explicit data-quality reason, never a financial breach."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise DataError(reason)


@contextmanager
def exact():
    with localcontext(Context(prec=128)) as ctx:
        ctx.traps[Inexact] = True
        yield


def decimal(value: object, *, money: bool = False, positive: bool = False) -> Decimal:
    pattern = r'-?(0|[1-9][0-9]*)\.[0-9]{2}' if money else r'-?(0|[1-9][0-9]*)(\.[0-9]{1,8})?'
    require(isinstance(value, str) and len(value) <= 40 and re.fullmatch(pattern, value) is not None,
            'invalid_money' if money else 'invalid_decimal')
    result = Decimal(value)
    require(not positive or result > 0, 'nonpositive_specification')
    return result


def cents(value: Decimal) -> Decimal:
    with exact():
        require(value.is_finite(), 'nonfinite_money')
        require(value % Decimal('0.01') == 0, 'fractional_cent')
        return value.quantize(Decimal('0.01'))


def money_text(value: Decimal | None) -> str | None:
    return None if value is None else format(cents(value), '.2f')


def integer(value: object, *, minimum: int = 0) -> int:
    require(type(value) is int and minimum <= value <= 1_000_000_000, 'invalid_integer')
    return value


def text(value: object) -> str:
    require(isinstance(value, str) and 0 < len(value) <= 512, 'invalid_identifier')
    return value


def timestamp(value: object) -> datetime:
    require(isinstance(value, str) and re.fullmatch(
        r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?Z', value) is not None,
        'invalid_timestamp')
    try:
        return datetime.fromisoformat(value).astimezone(timezone.utc)
    except ValueError as error:
        raise DataError('invalid_timestamp') from error


def fields(data: object, required: set[str], optional: set[str] = frozenset()) -> dict:
    require(type(data) is dict, 'expected_object')
    require(required <= data.keys() and data.keys() <= required | optional, 'invalid_fields')
    return data
