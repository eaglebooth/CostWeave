# CostWeave call guide

## Test constants

- Effective date: `2026-10-08`
- Denomination: `USD_CENTS` (one uppercase unit identifier binds every amount in the batch; no FX conversion)
- Source digest: read `canonical_sha256` from `TEST_RESOURCE_MANIFEST.json`
- Source: fixed by the contract to the dated 2 CFR 200.403 eCFR XML endpoint

## Sequence

1. Auxiliary wallet A calls `create_batch(local_id, reviewer, consumer,
   effective_date, denomination, lines_json)`.
2. Read `get_batch(batch_id)` and copy the returned `snapshot_digest`.
3. Auxiliary wallet B, the declared reviewer, calls
   `accept_batch(batch_id, snapshot_digest)`.
4. Any auxiliary wallet calls
   `compile_allocation(batch_id, 0, canonical_source_digest)`.
5. Read the same exact batch ID and verify generation, source digest, vector, all
   three totals, and `allowable + unallowable + review == total`.
6. Only the declared consumer may call `consume_compilation(batch_id, 1)`, and
   only when status is `COMPILED` rather than `REVIEW_REQUIRED`.

Main/deployer wallet has no privileged method. Reviewer tests should also execute
wrong reviewer, wrong digest, source failure, review-required, unauthorized consumer,
stale replay, and double-consumption paths with complete pre/post readback.

