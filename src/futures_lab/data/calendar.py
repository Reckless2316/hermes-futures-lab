"""Pinned explicit sessions; no guessed holidays, sessions or boundary fills."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from hashlib import sha256
from importlib import metadata
from pathlib import Path
from zoneinfo import TZPATH, ZoneInfo, ZoneInfoNotFoundError

from futures_lab.domain.events import canonical
from futures_lab.domain.values import DataError, fields, require, text, timestamp


def timezone_version() -> str:
    for base in TZPATH:
        path = Path(base) / "tzdata.zi"
        if path.exists():
            first = path.read_text().splitlines()[0]
            if first.startswith("# version "):
                return "iana-" + first.removeprefix("# version ")
    try:
        return "tzdata-" + metadata.version("tzdata")
    except metadata.PackageNotFoundError as error:
        raise DataError("timezone_version_unavailable") from error


@dataclass(frozen=True)
class Session:
    id: str
    start: datetime
    close: datetime


@dataclass(frozen=True)
class Calendar:
    id: str
    sessions: tuple[Session, ...]
    sha256: str
    tzdb_version: str
    original_bytes: bytes

    @classmethod
    def parse(cls, raw: object) -> "Calendar":
        d = fields(raw, {"id", "timezone", "sessions"})
        text(d["id"])
        require(d["timezone"] == "America/New_York", "unsupported_timezone")
        require(
            type(d["sessions"]) is list and len(d["sessions"]) > 0, "missing_calendar"
        )
        try:
            zone = ZoneInfo(d["timezone"])
        except ZoneInfoNotFoundError as error:
            raise DataError("timezone_data_unavailable") from error
        sessions: list[Session] = []
        seen: set[str] = set()
        for row in d["sessions"]:
            s = fields(row, {"session_id", "start_utc", "close_utc"})
            text(s["session_id"])
            try:
                day = date.fromisoformat(s["session_id"])
                require(day.isoformat() == s["session_id"], "invalid_session_id")
                expected_start = datetime.combine(
                    day - timedelta(days=1), time(18), zone
                )
            except (ValueError, OverflowError) as error:
                raise DataError("invalid_session_id") from error
            start, close = timestamp(s["start_utc"]), timestamp(s["close_utc"])
            require(
                start == expected_start,
                "invalid_session_start",
            )
            local_close = close.astimezone(zone)
            require(
                start < close
                and local_close.date() == day
                and local_close.time() <= time(16, 10),
                "invalid_session_close",
            )
            require(s["session_id"] not in seen, "duplicate_session")
            require(
                not sessions or start > sessions[-1].close,
                "overlapping_or_unordered_sessions",
            )
            seen.add(s["session_id"])
            sessions.append(Session(s["session_id"], start, close))
        wire = canonical(d).encode()
        return cls(
            d["id"], tuple(sessions), sha256(wire).hexdigest(), timezone_version(), wire
        )

    def session(self, session_id: str) -> Session:
        for session in self.sessions:
            if session.id == session_id:
                return session
        raise DataError("missing_calendar_coverage")

    def locate(self, stamp: datetime, kind: str) -> Session:
        for session in self.sessions:
            if session.start <= stamp < session.close:
                require(kind != "SessionClose", "premature_session_close")
                return session
            if stamp == session.close:
                require(kind == "SessionClose", "session_close_boundary_quarantine")
                return session
        raise DataError("outside_calendar_session")
