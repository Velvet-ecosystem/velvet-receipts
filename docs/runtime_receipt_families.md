# Runtime Receipt Families

Velvet Receipts is the canonical accountability layer for Runtime Court, safety, and execution evidence.

Supported Runtime receipt events are:

```text
COURT_AUTHORIZED
COURT_DENIED
SAFETY_APPROVED
SAFETY_DENIED
SAFETY_FAILED
EXECUTION_STARTED
EXECUTION_COMPLETED
EXECUTION_FAILED
EXECUTION_DENIED
```

Each Runtime receipt records:

- source
- subject identity
- intent identifier where available
- capability-token identifier where available
- capability
- target
- executor or safety-gate identity where available
- decision state
- errors and output evidence where available

All Runtime receipts carry the schema marker:

```text
velvet.runtime.receipt.v1
```

The canonical builder is `runtime_receipt_from_envelope()` in `runtime_receipts.py`.

A receipt records evidence. It does not authorize an action by itself. Court authorization, signed tokens, safety gates, approved executors, replay protection, and local policy remain separate mandatory controls.
