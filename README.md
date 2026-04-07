# Velvet Receipts

Provides receipt creation and logging for the Velvet ecosystem.

Used by enforcement systems such as velvet-event-protocol.

Receipts are not logs.

Logs capture activity.
Receipts preserve accountability.

Every decision Velvet makes can be traced, inspected, and verified —
including what happened, what policy governed it, and who authorized it.

A remembering machine cannot hide behind resets.

If memory exists, responsibility exists.

---

## Purpose

Velvet Receipts provides a minimal, deterministic, append-only system
for recording system decisions in a verifiable, hash-chained format.

Each receipt answers four questions:

1. What happened?
2. What decision was made, and what was the result?
3. Under what policy and authority was this sanctioned?
4. How does this connect to everything that came before?

---

## What a Receipt Contains

| Field | Description |
|---|---|
| `receipt_id` | Unique ID for this receipt (UUID) |
| `timestamp` | Unix timestamp of the decision |
| `event` | What triggered the decision |
| `decision` | What action was chosen |
| `result` | What the outcome was |
| `policy` | Named policy governing this decision |
| `authorized_by` | Authority that sanctioned the action (e.g. "Core") |
| `context` | Environmental/state data at decision time |
| `constraints` | Active constraints during the decision |
| `previous_hash` | Hash of the prior receipt (`"GENESIS"` if first) |
| `hash` | SHA-256 of this receipt's canonical payload |
| `notes` | Optional: freeform explanation |
| `confidence` | Optional: numeric or string confidence level |
| `domain` | Optional: subsystem domain (e.g. "lighting", "climate") |

---

## Hash Chaining

Each receipt's hash is computed from its own canonical payload,
which includes `previous_hash`.

This means:

- The first receipt chains to `"GENESIS"`
- Every subsequent receipt includes the prior receipt's hash
- Altering any receipt breaks all receipts that follow it
- The chain can be independently verified at any time

Hash function: SHA-256 over compact, sort-keyed JSON.

`hash` itself is never included in its own payload.

---

## Policy-Bound Accountability

Receipts are not just records of what happened.
They are records of what was permitted to happen, and by whom.

`policy` names the rule that governed the decision.
`authorized_by` names the authority that allowed it.

This matters for audits.
When a decision is later questioned, the receipt says:
this action was taken because this policy said so,
and this authority sanctioned it.

Velvet does not make undocumented decisions.

---

## What This Is Not

- Not a debug logger
- Not an analytics system
- Not an AI decision engine
- Not a policy enforcement layer
- Not a cryptographic signing infrastructure

---

## Chain Verification

```python
logger = ReceiptLogger()
valid, errors = logger.verify_chain()
```

`verify_chain()` loads every receipt and:

1. Recomputes each hash from its stored canonical payload
2. Confirms the stored hash matches
3. Confirms `previous_hash` matches the actual prior receipt's hash

Returns `(True, [])` if the chain is intact.
Returns `(False, [list of errors])` if anything has been altered or broken.

---

## Example

```python
from receipt import Receipt
from receipt_logger import ReceiptLogger

logger = ReceiptLogger()

r1 = Receipt(
    event="low_light_detected",
    decision="turn_on_headlights",
    result="headlights_on",
    policy="AutoHeadlightPolicy",
    authorized_by="Core",
    context={"ambient_light_lux": 12},
    constraints={"speed_kmh": "<= 120", "manual_override": False},
    domain="lighting",
)
logger.log(r1)

r2 = Receipt(
    event="driver_override",
    decision="defer_to_manual_control",
    result="headlights_manual",
    policy="DriverSovereigntyPolicy",
    authorized_by="Core",
    context={"override_source": "steering_column_stalk"},
    constraints={"manual_override": True},
    domain="lighting",
    notes="Driver assumes direct control.",
)
logger.log(r2)

valid, errors = logger.verify_chain()
```

---

## Design Principles

- Deterministic output
- Append-only logging
- Hash-chained integrity
- Policy-bound accountability
- No external dependencies
- Separation from decision-making systems

---

## License

GPLv3 — aligned with Velvet core infrastructure.

---

Velvet does not forget.

Every decision, every action, every state can be traced, inspected, and understood.

If intelligence exists inside the machine, it cannot hide behind the cloud.
Velvet makes that visible.
