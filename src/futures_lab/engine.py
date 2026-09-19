"""In-memory deterministic financial projection of normalized recorded events.

No fill simulation, network, database, execution routing or compliance inference.
"""

import copy
from dataclasses import dataclass, field
from decimal import Decimal
from hashlib import sha256
import json

from futures_lab.data.calendar import Calendar
from futures_lab.data.input import provenance
from futures_lab.domain.events import Event, Instrument, canonical
from futures_lab.domain.ledger import Journal, Position
from futures_lab.domain.values import DataError, decimal, exact, fields, money_text, require, text, timestamp
from futures_lab.rules.financial import Drawdown, consistency, exposure, target_met
from futures_lab.rules.manifest import Ruleset

ZERO = Decimal('0.00')


@dataclass
class Projection:
    specs: dict[str, Instrument] = field(default_factory=dict)
    positions: dict[str, Position] = field(default_factory=dict)
    orders: dict[str, Event] = field(default_factory=dict)
    order_states: dict[str, str] = field(default_factory=dict)
    filled: dict[str, int] = field(default_factory=dict)
    fills: dict[str, Event] = field(default_factory=dict)
    market: dict[str, Event] = field(default_factory=dict)
    marks: dict[str, tuple] = field(default_factory=dict)
    seen: set[str] = field(default_factory=set)
    gross: Decimal = ZERO
    fees: Decimal = ZERO
    days: dict[str, tuple[Decimal, Decimal]] = field(default_factory=dict)
    closed: set[str] = field(default_factory=set)
    session_id: str | None = None
    selected: bool = False
    assessed: bool = False
    # Observed excess requires unresolved-policy review even after flattening.
    exposure_evidence: list[str] = field(default_factory=list)
    breach_evidence: list[str] = field(default_factory=list)
    drawdown: Drawdown | None = None


class Engine:
    def __init__(self, rules: Ruleset, calendar: Calendar, source: dict, *, run_id: str,
                 code_version: str, input_sha256: str):
        self.rules, self.calendar = rules, calendar
        self._provenance = provenance(source)
        self.run_id, self.code_version = text(run_id), text(code_version)
        require(len(input_sha256) == 64 and all(c in '0123456789abcdef' for c in input_sha256),
                'invalid_input_hash')
        self.input_sha256 = input_sha256
        self._journal = Journal()
        self._projection = Projection(drawdown=Drawdown.initial_state(rules.initial, rules.drawdown))
        self._quarantine: list[dict] = []
        self._quality_history: list[dict] = []
        self._reports: list[str] = []
        self._clock = None

    @property
    def events(self) -> tuple[Event, ...]:
        return self._journal.events

    @property
    def checkpoints(self) -> tuple[dict, ...]:
        return tuple(json.loads(report) for report in self._reports)

    def _values(self, state: Projection, stamp) -> tuple[Decimal, Decimal | None, list[str]]:
        with exact():
            balance = self.rules.initial + state.gross - state.fees
            unrealized = ZERO
            missing = []
            for ident, position in state.positions.items():
                if position.quantity:
                    mark = state.marks.get(ident)
                    if mark is None or mark[1] != stamp:
                        missing.append('missing_current_mark:' + ident)
                    else:
                        unrealized += position.unrealized(mark[0], state.specs[ident])
            return balance, None if missing else unrealized, missing

    def append(self, raw: dict) -> dict:
        """Atomic financial application. Rejections are retained separately, never hidden."""
        event = None
        try:
            event = Event.parse(raw)
            if not self._journal.check(event):
                return {'disposition': 'duplicate', 'event_id': event.event_id}
            require(self._clock is None or event.time >= self._clock, 'event_before_clock')
            p = copy.deepcopy(self._projection)
            with exact():
                self._apply(p, event)
                balance, unrealized, missing = self._values(p, event.time)
                equity = None if unrealized is None else balance + unrealized
                financial = event.kind in {'Fill', 'Commission', 'PositionMark', 'SessionClose'}
                if financial:
                    before = p.drawdown.breached
                    p.drawdown = p.drawdown.observe(equity)
                    if p.drawdown.breached and not before:
                        p.breach_evidence.append(event.event_id)
                count = exposure(tuple((pos.quantity, self.rules.weight(p.specs[k].counting_class))
                                       for k, pos in p.positions.items()), self.rules.exposure_limit)
                if not count['within_cap'] and event.event_id not in p.exposure_evidence:
                    p.exposure_evidence.append(event.event_id)
                if event.kind == 'SessionClose':
                    # Cash is known even if equity/eligibility lacks mark coverage.
                    p.drawdown = p.drawdown.close(balance)
                    p.closed.add(event.session_id)
                    p.assessed = True
            self._journal.append(event)
            self._projection = p
            self._clock = event.time
            if financial and missing:
                self._quality_history.append({'event_id': event.event_id, 'reasons': missing})
            report = self.report()
            self._reports.append(canonical(report))
            return {'disposition': 'accepted', 'event_id': event.event_id, 'report': report}
        except DataError as error:
            record = {'reason': error.reason, 'event_id': event.event_id if event else
                      (raw.get('event_id') if type(raw) is dict and isinstance(raw.get('event_id'), str) else None),
                      'source_event_id': event.source_event_id if event else None,
                      'input_sha256': self.input_sha256,
                      'raw_event_sha256': raw_hash(raw)}
            self._quarantine.append(record)
            return {'disposition': 'quarantine', **record}

    def advance_to(self, utc: str) -> dict:
        """Derived calendar clock; never fabricates an imported event or a mark."""
        stamp = timestamp(utc)
        require(self._clock is None or stamp >= self._clock, 'clock_reversal')
        session = self.calendar.locate(stamp, 'Clock')
        p = copy.deepcopy(self._projection)
        self._enter_session(p, session.id)
        self._projection, self._clock = p, stamp
        return self.report()

    def _enter_session(self, p: Projection, session_id: str) -> None:
        if p.session_id != session_id:
            if p.session_id is not None:
                require(p.session_id in p.closed, 'missing_session_close')
                ids = [s.id for s in self.calendar.sessions]
                require(ids.index(session_id) == ids.index(p.session_id) + 1,
                        'missing_intermediate_session_close')
            p.drawdown = p.drawdown.start()
            p.session_id = session_id
            p.assessed = False

    def _apply(self, p: Projection, e: Event) -> None:
        data = e.payload
        source = json.loads(self._provenance)
        require(e.provenance_id == source['id'], 'missing_provenance')
        session = self.calendar.locate(e.time, e.kind)
        require(session.id == e.session_id, 'session_id_mismatch')
        require(e.session_id not in p.closed, 'event_after_session_close')
        self._enter_session(p, e.session_id)
        p.days.setdefault(e.session_id, (ZERO, ZERO))
        if e.kind == 'InstrumentSpec':
            spec = Instrument.from_event(e)
            require(spec.instrument_id in source['instrument_spec_ids'], 'undeclared_instrument')
            require(spec.instrument_id not in p.specs, 'duplicate_instrument')
            require(spec.calendar_id == self.calendar.id, 'instrument_calendar_mismatch')
            require(decimal(data['mini_equivalent']) == self.rules.weight(spec.counting_class),
                    'counting_class_weight_mismatch')
            p.specs[spec.instrument_id] = spec
        elif e.kind == 'RulesetSelected':
            require(not p.selected, 'multiple_rules_selections')
            require(data == {'ruleset_id': self.rules.id, 'rules_version': self.rules.version,
                             'ruleset_sha256': self.rules.sha256}, 'rules_selection_mismatch')
            p.selected = True
        else:
            require(p.selected, 'missing_rules_selection')
            if 'instrument_id' in data:
                ident = data['instrument_id']
                require(ident in p.specs, 'missing_instrument_spec')
                for key in {'price', 'limit_price', 'stop_price', 'bid', 'ask', 'open', 'high', 'low', 'close'} & data.keys():
                    p.specs[ident].check_price(decimal(data[key]))
            if e.kind == 'OrderIntent':
                require(data['order_id'] not in p.orders, 'duplicate_order_id')
                p.orders[data['order_id']] = e
                p.order_states[data['order_id']] = 'pending'
            elif e.kind in {'OrderAccepted', 'OrderRejected'}:
                order = p.orders.get(data['order_id'])
                require(order is not None and order.event_id == data['intent_event_id'], 'missing_order_intent')
                require(p.order_states[data['order_id']] == 'pending', 'duplicate_order_decision')
                p.order_states[data['order_id']] = 'accepted' if e.kind == 'OrderAccepted' else 'rejected'
            elif e.kind == 'Fill':
                order = p.orders.get(data['order_id'])
                require(order is not None and p.order_states[data['order_id']] == 'accepted', 'fill_without_acceptance')
                require(data['fill_id'] not in p.fills, 'duplicate_fill_id')
                require(all(data[k] == order.payload[k] for k in ('side', 'instrument_id')), 'fill_intent_mismatch')
                quantity = data['quantity']
                sofar = p.filled.get(data['order_id'], 0)
                require(sofar + quantity <= order.payload['quantity'], 'overfilled_order')
                price = decimal(data['price'])
                position, realized = p.positions.get(ident, Position()).fill(
                    quantity if data['side'] == 'buy' else -quantity, price, p.specs[ident], data['fill_id'])
                p.positions[ident] = position
                p.filled[data['order_id']] = sofar + quantity
                p.fills[data['fill_id']] = e
                p.gross += realized
                gross, fees = p.days[e.session_id]
                p.days[e.session_id] = gross + realized, fees
                # Recorded fill price values this instrument at that exact instant.
                # It never supplies a stale mark for another instrument or later time.
                p.marks[ident] = (price, e.time, e.event_id)
            elif e.kind == 'Commission':
                require(data['fill_id'] in p.fills, 'commission_without_fill')
                fee = decimal(data['amount'], money=True)
                p.fees += fee
                gross, fees = p.days[e.session_id]
                p.days[e.session_id] = gross, fees + fee
            elif e.kind == 'MarketEvent':
                if data['kind'] == 'quote':
                    require(decimal(data['bid']) <= decimal(data['ask']), 'crossed_quote')
                if data['kind'] == 'bar':
                    low, high = decimal(data['low']), decimal(data['high'])
                    require(low <= min(decimal(data['open']), decimal(data['close'])) <=
                            max(decimal(data['open']), decimal(data['close'])) <= high, 'invalid_bar')
                p.market[e.event_id] = e
            elif e.kind == 'PositionMark':
                market = p.market.get(data['market_event_id'])
                require(market is not None, 'missing_market_reference')
                require(market.payload['kind'] == 'trade', 'unsupported_mark_source')
                require(market.time == e.time, 'stale_mark_source')
                require(market.payload['instrument_id'] == ident and market.payload['price'] == data['price'],
                        'mark_source_mismatch')
                p.marks[ident] = (decimal(data['price']), e.time, market.event_id)
            elif e.kind == 'SessionClose':
                require(data['calendar_id'] == self.calendar.id, 'close_calendar_mismatch')
                require(set(p.specs) == set(source['instrument_spec_ids']), 'missing_instrument_spec')
            elif e.kind == 'JournalNote':
                require(all(ref in p.seen for ref in data['referenced_event_ids']), 'unknown_note_reference')
        p.seen.add(e.event_id)

    def report(self) -> dict:
        with exact():
            return self._report_exact()

    def _report_exact(self) -> dict:
        p, r = self._projection, self.rules
        source = json.loads(self._provenance)
        last = self.events[-1] if self.events else None
        if last:
            balance, unrealized, missing = self._values(p, self._clock)
        else:
            balance, unrealized, missing = r.initial, None, ['no_events']
        equity = None if unrealized is None else balance + unrealized
        gross_view = consistency(tuple(v[0] for _, v in sorted(p.days.items())), r.consistency_limit)
        net_view = consistency(tuple(v[0] - v[1] for _, v in sorted(p.days.items())), r.consistency_limit)
        positions = tuple((pos.quantity, r.weight(p.specs[k].counting_class)) for k, pos in p.positions.items())
        count = exposure(positions, r.exposure_limit)
        open_count = sum(pos.quantity != 0 for pos in p.positions.values())
        target = target_met(balance, r.initial, r.target, open_count, p.assessed)
        reasons = list(missing)
        if not p.selected:
            reasons.append('missing_rules_selection')
        if self._quarantine:
            reasons.append('quarantined_input')
        if self._quality_history:
            reasons.append('incomplete_valuation_history')
        if source['gaps']:
            reasons.append('declared_source_gaps')
        if p.exposure_evidence:
            reasons.append('exposure_consequence_unresolved')
        if p.drawdown.breached:
            state = 'breached'
        elif reasons:
            state = 'data_unavailable'
        elif target and net_view['satisfied']:
            state = 'eligible_estimate'
        else:
            state = 'not_yet_eligible'
        events_wire = '[' + ','.join(e.wire for e in self.events) + ']'
        return {
            'schema_version': 1, 'phase': 'P1', 'run_id': self.run_id,
            'account_id': last.account_id if last else None,
            'as_of_event_id': last.event_id if last else None,
            'as_of_utc': self._clock.isoformat().replace('+00:00', 'Z') if self._clock else None,
            'session_id': p.session_id, 'projection_revision': 1,
            'code_version': self.code_version, 'ruleset_id': r.id, 'rules_version': r.version,
            'ruleset_sha256': r.sha256, 'ruleset_review_status': 'pending',
            'rules_source_url': r.source_url, 'rules_source_observed_on': r.verified_on,
            'evaluation_mode': 'candidate_3_lab_estimate', 'authority': 'ADR-005-human-accepted-2026-09-19',
            'official_account_certification': False,
            'event_data_sha256': sha256(events_wire.encode()).hexdigest(),
            'input_sha256': self.input_sha256, 'calendar_sha256': self.calendar.sha256,
            'tzdb_version': self.calendar.tzdb_version, 'fill_model_version': None, 'seed': None,
            'provenance': source,
            'balance': money_text(balance), 'equity': money_text(equity),
            'realized_gross_pnl': money_text(p.gross), 'unrealized': money_text(unrealized),
            'fees': money_text(p.fees), 'target_progress': money_text(balance - r.initial),
            'floor': money_text(p.drawdown.floor),
            'buffer': money_text(None if equity is None else equity - p.drawdown.floor),
            'open_positions': open_count,
            'positions': [{'instrument_id': k, 'quantity': pos.quantity, 'counting_class': p.specs[k].counting_class}
                          for k, pos in sorted(p.positions.items()) if pos.quantity],
            'gross_consistency_share': gross_view, 'net_of_fees_consistency_share': net_view,
            'net_of_fees_label': 'lab_convention_pending_verification',
            'consistency_official_semantics': 'unresolved_pending_ftmo_confirmation',
            'exposure': {**count, 'limit': format(r.exposure_limit, '.1f'),
                         'classes': {k: format(v, '.1f') for k, v in r.classes},
                         'fractional_micro_summation': 'lab_convention_pending_ftmo_confirmation',
                         'policy_status': 'MANUAL_REVIEW' if p.exposure_evidence else 'no_observed_excess',
                         'evidence_event_ids': list(p.exposure_evidence)},
            'drawdown_breached': p.drawdown.breached, 'breach_evidence_event_ids': list(p.breach_evidence),
            'target_condition_met': target, 'after_session_close': p.assessed,
            'daily_loss_limit': None, 'state': state, 'data_quality_reasons': sorted(set(reasons)),
            'quarantine': copy.deepcopy(self._quarantine), 'valuation_gaps': copy.deepcopy(self._quality_history),
            'coverage': 'recorded_event_instants_only; continuous_equity_compliance_not_established',
            'practice_policy_status': 'not_implemented_p1', 'practice_policy_sha256': None,
            'qualitative_compliance_status': 'NOT_IMPLEMENTED_P1',
        }


def raw_hash(raw: object) -> str | None:
    try:
        return sha256(canonical(raw).encode()).hexdigest()
    except (TypeError, ValueError, RecursionError):
        return None


def evaluate_document(document: dict, rules: Ruleset, *, input_sha256: str,
                      code_version: str, run_id: str = 'lab-run') -> dict:
    """Evaluate a local normalized batch; return explicit unavailable for invalid envelopes."""
    try:
        d = fields(document, {'schema_version', 'fixture_id', 'provenance', 'calendar', 'events'},
                   {'expected_checkpoints'})
        require(type(d['schema_version']) is int and d['schema_version'] == 1, 'unknown_schema_version')
        text(d['fixture_id'])
        provenance(d['provenance'])
        calendar = Calendar.parse(d['calendar'])
        require(type(d['events']) is list and len(d['events']) <= 100_000, 'invalid_event_array')
        engine = Engine(rules, calendar, d['provenance'], run_id=run_id,
                        code_version=code_version, input_sha256=input_sha256)
        dispositions = [engine.append(event) for event in d['events']]
        return {'report': engine.report(), 'checkpoints': list(engine.checkpoints),
                'dispositions': [{k: v for k, v in item.items() if k != 'report'} for item in dispositions]}
    except DataError as error:
        return {'report': {'schema_version': 1, 'state': 'data_unavailable',
                           'reason': error.reason, 'input_sha256': input_sha256,
                           'ruleset_id': rules.id, 'rules_version': rules.version,
                           'ruleset_sha256': rules.sha256, 'evaluation_mode': 'candidate_3_lab_estimate',
                           'official_account_certification': False}, 'checkpoints': [], 'dispositions': []}
