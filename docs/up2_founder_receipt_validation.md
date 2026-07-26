# UP² Founder Receipt Validation

## Validation Scope

On July 26, 2026, `velvet-receipts` was installed from the local editable source tree and participated in Velvet's first verified Founder Runtime boot on physical UP² hardware.

The visible final posture was:

```text
Continuity        VERIFIED
Court             READY
Runtime           ACTIVE
Routes            READ-ONLY
Physical Control  DISABLED

Waiting for Mister
```

This validates package presence, import compatibility, and architectural fit inside the bounded Founder boot path.

It does not by itself prove that every displayed state was persisted as a canonical receipt in the append-only receipt chain.

## What Was Proven

The physical session established that:

- the `velvet-receipts` distribution could be installed in the same explicit Python environment as Runtime, Interface, AI Core, Event Protocol, Continuity Spine, and Vehicle CAN
- Runtime could reach the verified read-only Founder posture without Receipts becoming an authority or execution layer
- the ecosystem remained fail closed while dependencies, identity state, and snapshots were repaired
- the final Interface presentation distinguished verified state from physical authority
- the public receipt contracts remained compatible with the architecture exercised on the UP²

## What Was Not Yet Proven

The session did not yet establish all of the following:

- that one complete canonical boot receipt chain was persisted for the full startup sequence
- that every visible Founder status line maps to one named receipt or verified receipt-derived state
- that receipt hashes were independently verified after a cold restart
- that interrupted writes, storage exhaustion, corruption, rotation, and recovery preserve truth on the UP²
- that Runtime, Event Protocol, Continuity Spine, Interface, and Receipts agree on one final cross-repository boot receipt schema
- that screenshots or social posts are cryptographically linked to canonical receipts
- that trusted time, signatures, or hardware-backed integrity are present

Those remain separate milestones.

## Screenshot and Snapshot Boundary

A Founder window screenshot is useful operator evidence, but it is not automatically a canonical Velvet receipt.

A Runtime boot snapshot is a rendered or serialized view of known state. It may be stale, incomplete, copied, edited, or generated from development state.

Therefore:

```text
screenshot present != canonical receipt persisted
snapshot present != current Runtime state
receipt present != claim proven true
hash chain valid != external fact independently verified
```

The correct evidence path is:

```text
trusted producer observation or decision
  -> canonical receipt payload
  -> append-only receipt sink
  -> hash-chain verification
  -> optional snapshot or Interface presentation
```

Presentation should consume verified evidence. Presentation must not become the evidence source merely because it looks authoritative.

## Development-State Boundary

The verified Founder boot used Runtime's bounded local development state under `.velvet-dev/state`.

That state was suitable for read-only integration validation. It was not production identity provisioning, production retention policy, or a final immutable receipt store.

The session therefore proves that the receipt layer fits the development boot path. It does not certify production evidence retention.

## Interpreter and Editable Install Rule

The validated installation used one explicit interpreter:

```bash
PYTHON=/home/coyote/.pyenv/versions/3.10.20/bin/python3
$PYTHON -m pip install -e ~/velvet/velvet-receipts
```

All package checks, Runtime commands, snapshot generation, and Interface launch must use the same interpreter environment.

A successful install under another Python executable does not prove Runtime can import the package.

## Distribution and Import Identity

Operators should distinguish the package distribution name from Python import names.

The distribution appears in package inventory as:

```text
velvet-receipts
```

Runtime checks and Python code may use repository-specific import modules instead of the distribution label. Package discovery must not assume those names are identical.

## Fail-Closed Lessons

The physical bring-up demonstrated a useful diagnostic progression:

1. package absence or discovery failure was reported as blocked
2. continuity identity absence remained blocked
3. bounded development state was created explicitly
4. the environment was sourced in the active shell
5. the boot snapshot was regenerated from current state
6. the Interface displayed the resulting verified read-only posture

At no point did Receipts manufacture permission, identity, or successful actuation claims to clear a gate.

## Canonical Founder Boot Receipt Target

The next full validation should produce and independently verify a boot receipt sequence with explicit families for:

- boot initiated
- component inventory observed
- continuity verification completed or denied
- body, surface, profile, and session bindings loaded
- Court readiness established or denied
- Runtime mode selected
- route posture selected
- physical-control posture selected
- degraded or blocked reasons
- boot completed
- Interface snapshot rendered from the verified boot state

Each receipt must preserve whether it is:

- observation
- decision
- transition
- result
- degraded evidence

No receipt should imply physical execution when none occurred.

## Next Validation Milestones

1. Generate one canonical append-only receipt chain for a complete Founder boot.
2. Verify the chain after process restart and cold machine restart.
3. Map each Founder status line to named canonical evidence.
4. Test interrupted writes and truth-preserving degraded outcomes.
5. Add cross-repository boot receipt fixtures and compatibility tests.
6. Define bounded retention, rotation, export, and redaction rules for the Founder node.
7. Link optional operator screenshots to receipt hashes without treating the image as the receipt itself.
8. Validate the same evidence laws on Luckfox nodes.

## Authority Position

Current physical authority in `velvet-receipts`: **none**.

Receipts preserve evidence. They do not authorize requests, select executors, open hardware buses, or perform physical action.
