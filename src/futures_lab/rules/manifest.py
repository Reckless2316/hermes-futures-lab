"""Load only immutable candidate.3 under the human-approved ADR 005 lab mode."""

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from importlib.resources import files
from pathlib import Path

import yaml

from futures_lab.domain.values import DataError, decimal, require

CANDIDATE_NAME = 'ftmo_futures_growth_evaluation_50k_2026-09-18_candidate.3.yaml'
CANDIDATE_HASH = 'a1dcf3f3ac04abb7c5334bd6e65e9374fc36d67c3422a4b590c3ed3ae8eeeda6'


@dataclass(frozen=True)
class Ruleset:
    id: str
    version: str
    sha256: str
    original_bytes: bytes
    initial: Decimal
    target: Decimal
    drawdown: Decimal
    consistency_limit: Decimal
    classes: tuple[tuple[str, Decimal], ...]
    exposure_limit: Decimal
    source_url: str
    verified_on: str

    def weight(self, counting_class: str) -> Decimal:
        weights = dict(self.classes)
        require(counting_class in weights, 'unknown_counting_class')
        return weights[counting_class]


def load_rules(path: Path | None = None) -> Ruleset:
    try:
        raw = (path.read_bytes() if path is not None else
               files('futures_lab').joinpath('resources', 'rules', CANDIDATE_NAME).read_bytes())
    except OSError as error:
        raise DataError('rules_unavailable') from error
    digest = sha256(raw).hexdigest()
    require(digest == CANDIDATE_HASH, 'unapproved_rules_bytes')
    # Hash equality restricts input to the reviewed immutable document before parsing.
    d = yaml.safe_load(raw)
    counting = d['contract_counting']
    # Exactly one canonical exposure configuration. The legacy scalar supplies the
    # accepted numeric cap ONCE; it never defines weights or another counting path.
    # The class mapping/aggregation authority is solely candidate.3 contract_counting.
    return Ruleset(d['id'], d['rules_version'], digest, raw,
                   decimal(d['initial_balance'], money=True), decimal(d['profit_target'], money=True),
                   decimal(d['drawdown']['amount'], money=True),
                   decimal(d['consistency']['best_closed_profit_day_max_share']),
                   tuple((k, decimal(v)) for k, v in sorted(counting['classes'].items())),
                   decimal(d['max_contracts_mini_equivalent']), d['source_url'], d['verified_on'])
