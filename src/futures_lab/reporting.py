"""Reproducible implementation identity for local and installed-wheel reports."""

from hashlib import sha256
from pathlib import Path

from futures_lab import __version__


def code_version() -> str:
    root = Path(__file__).resolve().parent
    digest = sha256()
    for path in sorted(root.rglob("*.py")):
        digest.update(
            path.relative_to(root).as_posix().encode()
            + b"\0"
            + path.read_bytes()
            + b"\0"
        )
    return __version__ + "+sha256:" + digest.hexdigest()
