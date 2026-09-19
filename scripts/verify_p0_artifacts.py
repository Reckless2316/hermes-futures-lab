"""Validate P0 artifact contracts and integrity; never evaluate financial rules."""

import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

FORMATS = FormatChecker()


@FORMATS.checks('date-time', raises=ValueError)
def utc_timestamp(value):
    # jsonschema's optional RFC3339 dependency is absent. Validate explicitly
    # rather than silently accepting invalid timestamps through a no-op format.
    if not isinstance(value, str):
        return True  # The schema's type constraint rejects non-strings.
    if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?Z', value) is None:
        return False
    datetime.fromisoformat(value)
    return True

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_RULES = 'rules/ftmo_futures_growth_evaluation_50k_2026-09-17.yaml'
CANDIDATE_TWO_RULES = 'rules/ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.2.yaml'
CANDIDATE_TWO_HASH = '2da332b5627dee4585555e7af9cc375d8b1ab65107dba54b4c17d538b71179eb'
ACTIVE_RULES = 'rules/ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.3.yaml'
HISTORICAL_HASH = 'c835db6b7f455c7df4a246827ab77653f94a0dc4af92c25ec20634fd826ea750'
PAIRS = [
    (HISTORICAL_RULES, 'rules/schema.json'),
    (CANDIDATE_TWO_RULES, 'rules/schema.json'),
    (ACTIVE_RULES, 'rules/schema.json'),
    ('tests/fixtures/round_trip.json', 'tests/fixtures/trace.schema.json'),
    ('tests/fixtures/growth_50k_reference.json', 'tests/fixtures/reference.schema.json'),
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_mapping(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'Duplicate mapping key: {key}')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f'Non-finite JSON number: {value}')


class UniqueSafeLoader(yaml.SafeLoader):
    """Safe YAML with duplicate-key rejection for authored manifests."""


def yaml_mapping(loader, node):
    return unique_mapping((loader.construct_object(k), loader.construct_object(v))
                          for k, v in node.value)


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, yaml_mapping)


def read_artifact(path):
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.yaml':
        return yaml.load(text, Loader=UniqueSafeLoader)
    return json.loads(text, object_pairs_hook=unique_mapping, parse_constant=reject_constant)


def validate_schema(data, schema_file):
    schema = read_artifact(ROOT / schema_file)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FORMATS).validate(data)


def validate_trace(trace, manifest, rules_hash):
    """Check the authored trace subset; this is not a general P1 importer."""
    validate_schema(trace, 'tests/fixtures/trace.schema.json')
    calendar = trace['calendar']
    sessions = {s['session_id']: s for s in calendar['sessions']}
    require(len(sessions) == len(calendar['sessions']), 'Duplicate session')
    seen, imports, specs, orders, accepted, fills = {}, set(), {}, {}, set(), {}
    previous_time, selected = None, False
    accounts = set()
    for sequence, event in enumerate(trace['events'], 1):
        event_id, kind, payload = event['event_id'], event['event_type'], event['payload']
        require(event_id not in seen, 'Duplicate event ID')
        key = (event['account_id'], event['source'], event['source_event_id'])
        require(key not in imports, 'Duplicate import key in normalized fixture')
        imports.add(key)
        accounts.add(event['account_id'])
        require(len(accounts) == 1, 'Fixture must describe one account stream')
        require(event['sequence'] == sequence, 'Unexpected fixture sequence')
        stamp = datetime.fromisoformat(event['timestamp_utc'])
        require(previous_time is None or stamp >= previous_time, 'Out-of-order timestamp')
        previous_time = stamp
        require(event['session_id'] in sessions, 'Unknown session')
        session = sessions[event['session_id']]
        start, close = (datetime.fromisoformat(session[k]) for k in ('start_utc', 'close_utc'))
        require(start < close, 'Invalid session window')
        require(stamp == close if kind == 'SessionClose' else start <= stamp < close,
                'Event outside its session')
        require(event['provenance_id'] == trace['provenance']['id'], 'Unknown provenance')
        if kind == 'InstrumentSpec':
            require(payload['instrument_id'] not in specs, 'Duplicate instrument')
            require(payload['calendar_id'] == calendar['id'], 'Unknown instrument calendar')
            require(payload['currency'] == manifest['currency'], 'Instrument currency mismatch')
            tick, value, multiplier = (Decimal(payload[k]) for k in
                                       ('tick_size', 'tick_value', 'multiplier'))
            require(tick > 0 and value > 0 and multiplier > 0, 'Nonpositive tick specification')
            require(tick * multiplier == value, 'Inconsistent tick specification')
            weight = manifest['contract_counting']['classes'][payload['ftmo_counting_class']]
            require(payload['mini_equivalent'] == weight, 'Counting class/equivalence mismatch')
            specs[payload['instrument_id']] = payload
        elif kind == 'RulesetSelected':
            require(not selected, 'Multiple rules selections')
            require(payload == {'ruleset_id': manifest['id'], 'rules_version': manifest['rules_version'],
                                'ruleset_sha256': rules_hash}, 'Rules selection mismatch')
            selected = True
        else:
            require(selected, 'Rules must precede financial trace events')
            if 'instrument_id' in payload:
                require(payload['instrument_id'] in specs, 'Unknown instrument')
                if 'price' in payload:
                    tick = Decimal(specs[payload['instrument_id']]['tick_size'])
                    require(Decimal(payload['price']) % tick == 0, 'Off-tick price')
            if kind == 'OrderIntent':
                require(payload['order_id'] not in orders, 'Duplicate order ID')
                orders[payload['order_id']] = event
            elif kind == 'OrderAccepted':
                intent = orders.get(payload['order_id'])
                require(intent is not None and intent['event_id'] == payload['intent_event_id'],
                        'Unknown order intent')
                require(payload['order_id'] not in accepted, 'Duplicate order acceptance')
                accepted.add(payload['order_id'])
            elif kind == 'Fill':
                require(payload['order_id'] in accepted, 'Fill lacks preceding acceptance')
                require(payload['fill_id'] not in fills, 'Duplicate fill ID')
                intent = orders[payload['order_id']]['payload']
                require(all(payload[k] == intent[k] for k in ('instrument_id', 'side')),
                        'Fill differs from accepted intent')
                filled = sum(f['quantity'] for f in fills.values() if f['order_id'] == payload['order_id'])
                require(filled + payload['quantity'] <= intent['quantity'], 'Overfilled intent')
                fills[payload['fill_id']] = payload
            elif kind == 'Commission':
                require(payload['fill_id'] in fills, 'Commission lacks preceding fill')
            elif kind == 'PositionMark':
                market = seen.get(payload['market_event_id'])
                require(market is not None and market['event_type'] == 'MarketEvent',
                        'Mark lacks preceding market event')
                require(all(payload[k] == market['payload'][k] for k in ('instrument_id', 'price')),
                        'Mark differs from cited market event')
            elif kind == 'SessionClose':
                require(payload['calendar_id'] == calendar['id'], 'Unknown close calendar')
        seen[event_id] = event
    require(selected, 'Missing rules selection')
    require(set(specs) == set(trace['provenance']['instrument_spec_ids']), 'Provenance specs mismatch')
    require(all(c['after_event_id'] in seen for c in trace['expected_checkpoints']), 'Unknown checkpoint')


def validate_references(reference, manifest):
    validate_schema(reference, 'tests/fixtures/reference.schema.json')
    require(reference['source_url'] == manifest['source_url'], 'Reference source mismatch')
    require(reference['source_observed_on'] == manifest['verified_on'], 'Source date mismatch')
    ids = [case['id'] for case in reference['cases']]
    require(len(set(ids)) == len(ids), 'Duplicate reference case ID')
    for case in reference['cases']:
        if case['kind'] == 'consistency_fees':
            inputs = case['inputs']
            lengths = [len(inputs[k]) for k in ('gross_days', 'fees_by_day')]
            lengths.append(len(case['expected']['net_days']))
            if 'open_positions_by_day' in inputs:
                lengths.append(len(inputs['open_positions_by_day']))
            require(len(set(lengths)) == 1, 'Fee-vector day counts differ')


def main():
    for artifact, schema_file in PAIRS:
        validate_schema(read_artifact(ROOT / artifact), schema_file)
        print('PASS schema:', artifact)
    inventory = read_artifact(ROOT / 'tests/fixtures/artifacts.sha256.json')
    required = {p for pair in PAIRS for p in pair} | {'tests/fixtures/README.md'}
    require(set(inventory) == required, 'Incomplete or unexpected artifact inventory')
    for path, expected in inventory.items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
                f'Artifact hash mismatch: {path}')
    require(inventory[HISTORICAL_RULES] == HISTORICAL_HASH, 'Historical manifest changed')
    require(inventory[CANDIDATE_TWO_RULES] == CANDIDATE_TWO_HASH, 'Candidate.2 changed')
    trace = read_artifact(ROOT / 'tests/fixtures/round_trip.json')
    manifest = read_artifact(ROOT / ACTIVE_RULES)
    validate_trace(trace, manifest, inventory[ACTIVE_RULES])
    provenance = trace['provenance']
    require(provenance['input_path'] == 'tests/fixtures/README.md', 'Unexpected recipe path')
    require(provenance['input_sha256'] == inventory[provenance['input_path']], 'Recipe hash mismatch')
    validate_references(read_artifact(ROOT / 'tests/fixtures/growth_50k_reference.json'), manifest)
    print(f'PASS {len(inventory)} exact-byte hashes, both historical manifests, trace and vector references')


if __name__ == '__main__':
    main()
