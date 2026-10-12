# CostWeave specification

Proof obligation: classify each mutually accepted expense-line declaration against
the general factors in the exact point-in-time text of 2 CFR 200.403, then conserve
the complete amount vector across allowable-declaration, unallowable-declaration,
and review-required buckets.

All line amounts share one batch-level denomination identifier (for example
`USD_CENTS`). The identifier and every line are bound into the reviewer-accepted
snapshot. CostWeave performs no currency conversion and rejects mixed-unit
interpretations by construction.

The source proves regulation text only. The two parties prove only mutual acceptance
of declared text. Neither proves real expense facts, documentation, award-specific
terms, accounting treatment, compliance, payment eligibility, or legal allowability.
Stored supporting excerpts are diagnostic evidence from the leader response; validator
agreement is bound to line ID, verdict, and criterion, not exact excerpt wording.

The contract fixes origin/path and rejects non-200 responses, but the GenVM web API
does not expose a final redirect URL or response Content-Type to the contract. The
offline acquisition tool rejects redirects and non-XML Content-Type. Effective-date
format is checked syntactically; an impossible/unavailable dated endpoint fails closed.

Unlike advisory applicability oracles, CostWeave compiles a bounded atomic allocation
vector and enforces total conservation. It does not maintain CVE/asset queries,
refresh an oracle head, route document corrections, or issue safety clearance.

