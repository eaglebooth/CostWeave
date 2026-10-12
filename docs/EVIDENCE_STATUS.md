# Evidence status

## Available now

- Exact contract source and generated SDK schema.
- Official point-in-time eCFR raw XML and canonical projection.
- Test Resource Manifest with authority, object, revision, digests, expected parser
  result, mutability, retrieval time, and explicit proof limitations.
- Predeclared Test Control Manifest covering negative, unavailable, changed-content,
  cross-object, malformed, authorization, and replay controls.
- Direct Mode behavioral tests, captured-validator differential test, linter output,
  schema output, and machine-readable local verification report.

## Live evidence now available

- StudioNet address and `get_version` identity readback.
- Fourteen finalized transactions covering happy, review-required, digest failure,
  authorization, snapshot failure, generation replay and double consumption.
- Twenty-six machine assertions, including exact pre/post equality for every expected
  business-error transaction.
- Canonical final readback for both `CONSUMED` and `REVIEW_REQUIRED` branches.

## Still not established

- Deployment transaction hash and byte-for-byte deployed-source parity. Runtime
  identity is established by the deployed `get_version` readback, not source bytes.
- A deliberately induced live validator disagreement/no-consensus case.
- Independent live security audit.

Local captured-validator differential checks do not prove network no-consensus
rollback. Local evidence must not be described as live GenVM network consensus.
