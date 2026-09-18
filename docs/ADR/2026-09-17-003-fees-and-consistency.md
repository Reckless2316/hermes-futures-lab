# ADR 003: Commission accounting and daily consistency

Date: 2026-09-17. Status: **human accepted the proposed lab convention**;
independent review pending.
Source: [FTMO Futures rules](https://ftmo.com/en/futures/trading-objectives-and-rules/),
Growth / Evaluation / Consistency, retrieved 2026-09-17.

The public explanation gives equity as balance plus open P&L minus commissions.
The consistency example uses daily closed profits, without specifying how entry
fees on still-open trades or subsequently posted fees are assigned to days.
Those choices can change eligibility. No account-specific agreement was supplied.

Accepted lab convention: record every fee once, at its event timestamp. Cash
balance is initial cash plus realized gross P&L minus posted fees. Equity is that
net cash balance plus marked unrealized P&L; do not subtract fees a second time.
Closed daily profit for consistency is realized gross P&L minus **all fees posted
in that session**, including entry fees. Carrying positions across session close
never creates realized P&L. Corrections preserve the original fee's effective
session in a new projection revision.

Decision vector: daily gross closed profits [1200, 900, 900], with 30 of fees
posted on day three, produce net days [1200, 900, 870]. Gross accounting gives
1200/3000 = 40%, while the proposal gives 1200/2970 > 40%. Add later profit to
reach the target separately; this vector isolates the consistency objective.

Human decision, 2026-09-17, in this implementation session:
“Accept the proposed net-of-fees convention for the lab”. The proposed convention
above is therefore accepted for lab accounting. This is not verification of
account-specific FTMO terms. Independent review remains required.

Implementation record, 2026-09-18: candidate.1 remains byte-identical to the
checkpoint. New `2026-09-18-candidate.2` records this lab convention and the human
decision date. Its external source observation remains 2026-09-17 and independent
review remains pending. The schema, active trace, reference decision metadata and
artifact inventory now refer to candidate.2. Reviewed promotion must create a
new file/version; neither candidate is an accepted evaluation ruleset.
