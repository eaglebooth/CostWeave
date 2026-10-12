# CostWeave — Point-in-Time Cost Declaration Compiler

CostWeave is a contract-only GenLayer Intelligent Contract. Two wallets accept an
exact bounded expense-line batch. Validators read a point-in-time eCFR snapshot of
2 CFR 200.403 and compile an atomic line-by-line declaration vector with conserved
totals. A designated consumer may acknowledge a fully compiled vector exactly once.
Every amount uses the single denomination committed in that batch (for example
`USD_CENTS`); the contract does not perform FX or unit conversion.

This is not an accounting system, legal determination, payment approval, or proof
that declared facts are true. `ALLOWABLE_DECLARATION` means only that the accepted
line text explicitly states facts aligned with one cited general criterion. Missing
award-specific limitations or facts must route to `REVIEW_REQUIRED`.

## Architecture

`DRAFT -> ACCEPTED -> COMPILED | REVIEW_REQUIRED -> CONSUMED`

- Main/deployer wallet has no role.
- Every consequential field is bound in a reviewer-accepted snapshot digest.
- Source is a fixed-origin, dated eCFR endpoint; caller cannot provide a URL.
- Consensus returns a bounded vector, not a single applicability verdict.
- Contract derives three amount totals and enforces exact conservation.
- Compilation is immutable and single-use; edits require a new batch.

## Verify

```powershell
python scripts/acquire_source.py
python scripts/verify.py
```

Local Direct Mode is not live consensus. StudioNet evidence is required after the
contract is deployed.

## StudioNet deployment

- Contract: [`0x9B5193244a8a97A2f94d09eF2B1F9697c34f0741`](https://explorer-studio.genlayer.com/address/0x9B5193244a8a97A2f94d09eF2B1F9697c34f0741)
- Live evidence: [`docs/LIVE_STUDIONET_EVIDENCE.md`](docs/LIVE_STUDIONET_EVIDENCE.md)
- Machine receipts: [`docs/live-evidence/studionet-261012.json`](docs/live-evidence/studionet-261012.json)

The live run used only two auxiliary wallets after deployment. The deployer did
not participate in the test lifecycle.

