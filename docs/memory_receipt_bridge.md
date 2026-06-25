# Memory and Receipt Bridge

## Purpose

This document defines how Velvet memory records and Velvet receipts refer to one another without collapsing their responsibilities.

## Boundary

Memory preserves experience, observations, conversations, inferences, accepted facts, decisions, outcomes, and continuity anchors.

Receipts preserve accountability for governed decisions and outcomes, including policy, authority, constraints, result, and chain integrity.

A memory record is not a receipt.

A receipt is not the private memory store.

## Linking rule

When a governed memory has an accountability record:

- the memory record stores the receipt's `receipt_id`
- the receipt stores the memory record's `event_id` in `context`
- both identifiers remain stable
- neither record copies more private content than required

Example receipt context:

```json
{
  "memory_event_id": "c04bc60d-53af-4fcb-a661-57f72941f3b8",
  "memory_kind": "decision"
}
```

Example memory metadata:

```json
{
  "event_id": "c04bc60d-53af-4fcb-a661-57f72941f3b8",
  "kind": "decision",
  "receipt_id": "4fb2a1a7-b51d-4a8f-a95f-3e17cbddb94f",
  "authority_status": "accepted"
}
```

## When a receipt is required

A receipt should be created when memory refers to:

- an authorization decision
- a policy-governed decision
- an executor command or outcome
- an identity or binding change
- a body-registry change
- a safety intervention
- a degraded-state transition
- a continuity recovery decision

A receipt is not required for every raw observation, conversational fragment, indexing tag, or private associative link.

## Confidence

Receipt `confidence` and memory `confidence` may share a numeric value, but they express different contexts.

- memory confidence expresses uncertainty about a remembered claim or interpretation
- receipt confidence expresses confidence relevant to the governed decision or outcome

Neither value grants authority.

## Corrections and supersession

Memory corrections are appended as new linked memory events.

Receipt corrections are appended as new receipts or follow-up governed records according to receipt-chain policy.

Existing memory events and receipts are never silently rewritten.

## Privacy

Receipt context should contain only the minimum public-safe or audit-required memory metadata.

Raw conversation text, intimate context, biometric detail, and private narrative should remain in the local memory layer unless an explicit policy permits inclusion.

## Doctrine

Receipts preserve accountability.

Memory preserves experience.

Stable identifiers let both systems describe the same history without becoming the same system.
