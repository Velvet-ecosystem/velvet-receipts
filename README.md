# Velvet Receipts

**Append-only evidence, accountability, and verifiable history for the Velvet ecosystem.**

Receipts are not logs.

Logs capture activity. Receipts preserve accountability.

A receipt records what was observed, proposed, authorized, denied, attempted, completed, degraded, or failed. It also preserves the policy, identity, execution, resource, and continuity context needed to explain why.

> Runtime decides what may proceed. Executors act. Receipts preserve the evidence.

## Purpose

Velvet Receipts provides a minimal, deterministic, append-only system for recording ecosystem decisions and outcomes in a hash-chained format.

Each receipt should help answer:

1. What happened?
2. What was requested or observed?
3. What decision was made?
4. Which identity, policy, capability, contract, and resource context applied?
5. Did execution or actuation actually occur?
6. What failed, degraded, or remained uncertain?
7. How does this evidence connect to the preceding chain?

A remembering machine cannot hide behind resets. If continuity exists, responsibility follows.

## Receipts Are Evidence, Not Authority

A receipt never grants permission by itself.

```text
receipt present != action authorized
receipt absent != action did not happen
memory present != identity verified
successful request != successful actuation
```

Authorization belongs to Runtime and Court. Execution belongs to approved executors. Resource ownership belongs to Runtime coordination. Receipts preserve the resulting evidence.

A malicious or mistaken component must not be able to manufacture authority merely by writing an impressive-looking receipt.

## Ecosystem Position

```text
verified identity and intent
  -> Runtime and Court
  -> execution contract
  -> resource coordination
  -> safety and replay gates
  -> approved executor
  -> receipt sink
  -> append-only evidence chain
```

Velvet Receipts is consumed by Runtime, continuity, event, interface, diagnostic, and audit tooling. It remains separate from the systems that decide or execute.

## Receipt Chain Contract

The receipt chain may preserve evidence for:

- boot identity and continuity verification
- body, profile, session, and surface binding
- Court authorization and denial
- policy selection and reason codes
- execution-contract validation
- resource acquisition, conflict, release, and release failure
- safety approval and denial
- replay rejection
- executor start, completion, denial, and failure
- degraded or recovery states
- read-only CAN observations and signal summaries
- Ghost Car synthetic observations
- operator correction and manual override evidence

Receipts record what occurred. They do not authorize actions by themselves.

See [Receipt Chain Contract](docs/receipt_chain_contract.md).

## Current Receipt Families

The wider Velvet Runtime currently emits or recognizes families including:

### Court

```text
COURT_AUTHORIZED
COURT_DENIED
```

These preserve the requested capability, target, identity context, selected policy set, stable reason code, and explanation.

### Resource coordination

```text
RESOURCE_ACQUIRED
RESOURCE_DENIED
RESOURCE_RELEASED
RESOURCE_RELEASE_FAILED
```

These preserve the execution owner, complete requested resource set, named conflicts, and release outcome.

### Execution

```text
EXECUTION_STARTED
EXECUTION_COMPLETED
EXECUTION_FAILED
EXECUTION_DENIED
```

These preserve the token, intent, executor, execution contract, parameters, result state, and whether execution or physical actuation actually occurred.

### Continuity and recovery

Continuity and recovery receipt types preserve identity lineage, active body or surface binding, verification failure, and degraded startup evidence.

### Observation

Observation receipts preserve read-only evidence such as Runtime status, host telemetry, CAN frames, decoded signal summaries, and synthetic Ghost Car fixtures.

Not every receipt family requires a dedicated constructor in this repository today. The repository provides the canonical evidence and chain model while producers remain responsible for their domain-specific payload contracts.

## Truth-Preserving Outcomes

Receipts must preserve the strongest known truth, including awkward truth.

If an executor physically acted and the final receipt write later failed, the result must not be rewritten as though nothing happened. The correct record is degraded evidence:

```text
execution_performed: true
actuation_performed: true or false as observed
receipt_persisted: false
state: degraded or unreceipted
```

Likewise, authorization does not prove execution, and an execution-start receipt does not prove completion.

Velvet must distinguish:

- proposed
- authorized
- denied
- started
- completed
- failed
- released
- degraded
- unknown

That distinction is essential for diagnostics, safety review, and future self-debugging.

## What a Receipt Contains

The base receipt model contains:

| Field | Description |
|---|---|
| `receipt_id` | Unique receipt identifier |
| `timestamp` | Time the evidence was recorded |
| `event` | Trigger or event family |
| `decision` | Decision or transition recorded |
| `result` | Observed outcome |
| `policy` | Policy or policy set associated with the decision |
| `authorized_by` | Verified authority source, not merely the proposing component |
| `context` | Identity, body, surface, environment, and state context |
| `constraints` | Active limits, contracts, gates, or safety conditions |
| `previous_hash` | Prior receipt hash, or `GENESIS` for the first record |
| `hash` | SHA-256 of the canonical receipt payload |
| `notes` | Optional explanation |
| `confidence` | Optional confidence value or label |
| `domain` | Optional subsystem domain |

Domain payloads may additionally include:

```text
profile_id
session_id
body_id
surface
intent_id
token_id
capability
target
court_reason_code
contract_id
executor_name
resource_owner_id
resources
conflicts
execution_performed
actuation_performed
receipt_persisted
errors
```

Sensitive values such as signing keys, secrets, raw credentials, or unnecessary private data must never be copied into receipts.

## Hash Chaining

Each receipt hash is computed from its canonical payload, including `previous_hash`.

- The first receipt chains to `GENESIS`.
- Every subsequent receipt includes the preceding receipt hash.
- Altering one receipt breaks verification for that receipt and the chain that follows.
- The chain can be independently inspected and verified.

The current hash function is SHA-256 over compact, sort-keyed JSON. The `hash` field is excluded from its own hash payload.

Hash chaining provides tamper evidence. It is not the same as signatures, secure hardware, trusted time, or remote notarization.

## Chain Verification

```python
logger = ReceiptLogger()
valid, errors = logger.verify_chain()
```

Verification:

1. recomputes each canonical hash
2. compares the stored hash
3. checks each `previous_hash` against the actual prior receipt
4. reports broken or malformed chain entries

Returns `(True, [])` when the chain is intact and `(False, errors)` when evidence is altered or broken.

## Example: Recording a Court Decision

```python
from receipt import Receipt
from receipt_logger import ReceiptLogger

logger = ReceiptLogger()

receipt = Receipt(
    event="COURT_AUTHORIZED",
    decision="authorize_read_only_can_observation",
    result="capability_token_issued",
    policy="owner-default",
    authorized_by="velvet-runtime.court",
    context={
        "profile_id": "owner",
        "session_id": "session-1",
        "body_id": "tiburon_v0",
        "surface": "drive",
        "intent_id": "intent-00042",
        "capability": "vehicle.can.observe",
        "target": "vehicle-can",
    },
    constraints={
        "read_only": True,
        "physical_actuation_allowed": False,
        "court_reason_code": "authorized",
    },
    domain="authorization",
)

logger.log(receipt)
valid, errors = logger.verify_chain()
```

This records an authorization decision. It does not open a CAN bus, run an executor, transmit a frame, or grant physical authority to the receipt library.

## Public Ghost CAN Receipts

Velvet Receipts can record the public Ghost CAN observation used by the synthetic vehicle demo.

Supported event:

```text
vehicle.can.ghost_observation
```

The constructor requires the evidence payload to remain explicitly synthetic and read-only:

```json
{
  "route_id": "can-ghost",
  "target": "vehicle-can-ghost",
  "read_only": true,
  "synthetic_fixture": true,
  "physical_bus_opened": false,
  "can_transmission_attempted": false,
  "actuation_performed": false,
  "authority_granted": false
}
```

Unsafe or missing boundary flags are rejected. The receipt records a synthetic observation only. It does not authorize CAN injection, open hardware buses, select executors, or perform actuation.

See [Ghost CAN Receipt Contract](docs/ghost_can_receipt_contract.md).

## Policy-Bound Accountability

Receipts should name the policy and verified authority context that governed a decision.

That allows later review to ask:

- Which policy set was evaluated?
- Which reason code was returned?
- Was owner, medical, emergency, guest, service, OEM, or remote authority active?
- Did identity context match the active body and session?
- Which execution contract applied?
- Which resources were held?
- Did the executor act?
- Was the final receipt persisted?

The proposing AI, organ, interface, or module is not automatically the authorizing authority.

## Privacy and Retention

Accountability does not require indiscriminate surveillance.

Receipt producers should:

- record only context required to explain the decision
- avoid raw audio, video, credentials, and unnecessary personal data
- use references or hashes for large evidence objects where appropriate
- support local retention and rotation policy
- preserve medically or legally sensitive evidence under stricter access controls
- keep local-first ownership as the default

Velour may index and explain receipt history, but the original chain should remain immutable and separately verifiable.

## What This Is Not

- not a debug logger
- not an analytics or advertising system
- not an AI reasoning engine
- not Court or policy enforcement
- not an executor
- not a resource coordinator
- not proof that an action occurred merely because a receipt claims it
- not a replacement for signatures, secure hardware, or trusted timestamps

## Design Principles

- deterministic canonical output
- append-only evidence
- hash-chained integrity
- policy-bound accountability
- truth-preserving degraded states
- local-first storage
- minimal dependencies
- separation from authorization and execution
- inspectable by humans and machines

## Current Status

The repository currently provides the base receipt model, append-only logger, chain verification, and bounded Ghost CAN receipt support.

The broader ecosystem now produces richer Court, execution, resource, continuity, and observation receipts. Their canonical cross-repository schema alignment remains active work.

Current physical authority: **none**.

## Next Milestones

1. Align canonical field names across Runtime, Event Protocol, Continuity Spine, and Interface.
2. Add explicit schema profiles for Court, resource, execution, observation, and recovery receipt families.
3. Add deterministic validation for execution and resource outcome truth fields.
4. Add bounded receipt query and explanation contracts for Velour.
5. Define retention, rotation, export, and redaction policy without breaking chain evidence.
6. Add cross-repository compatibility diagnostics and fixture bundles.
7. Evaluate optional signatures or local hardware-backed integrity without making cloud trust mandatory.

## License

GPLv3, aligned with Velvet's public core infrastructure.

---

Velvet does not forget.

Every decision, denial, action, failure, and correction can be traced, inspected, and understood.

If intelligence exists inside the machine, it cannot hide behind the cloud. Receipts make the evidence visible.
