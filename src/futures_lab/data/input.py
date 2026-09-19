"""Bounded JSON decoding and provenance validation; inputs are never executable."""

import json
import re
from hashlib import sha256
from pathlib import Path

from futures_lab.domain.events import canonical
from futures_lab.domain.values import DataError, fields, require, text


def pairs(items):
    d = {}
    for key, value in items:
        require(key not in d, 'duplicate_json_key')
        d[key] = value
    return d


def invalid_constant(value):
    raise DataError('nonfinite_json')


def decode(raw: bytes) -> dict:
    require(len(raw) <= 32_000_000, 'input_too_large')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        if isinstance(error, DataError):
            raise
        raise DataError('invalid_json') from error


def load_document(path: Path) -> tuple[dict, str]:
    try:
        with path.open('rb') as stream:
            raw = stream.read(32_000_001)
    except OSError as error:
        raise DataError('input_unavailable') from error
    return decode(raw), sha256(raw).hexdigest()


def provenance(raw: object) -> str:
    p = fields(raw, {'id', 'vendor', 'dataset_id', 'input_path', 'input_sha256', 'license', 'synthetic',
                     'original_timezone', 'adapter_version', 'instrument_spec_ids', 'gaps', 'correction_policy'})
    for key in set(p) - {'synthetic', 'instrument_spec_ids', 'gaps'}:
        text(p[key])
    require(re.fullmatch(r'[a-f0-9]{64}', p['input_sha256']) is not None, 'invalid_provenance_hash')
    require(type(p['synthetic']) is bool, 'invalid_provenance')
    require(type(p['instrument_spec_ids']) is list and len(p['instrument_spec_ids']) > 0, 'missing_instrument_specs')
    for value in p['instrument_spec_ids']:
        text(value)
    require(len(set(p['instrument_spec_ids'])) == len(p['instrument_spec_ids']), 'duplicate_provenance_spec')
    require(type(p['gaps']) is list, 'invalid_provenance_gaps')
    for value in p['gaps']:
        text(value)
    return canonical(p)
