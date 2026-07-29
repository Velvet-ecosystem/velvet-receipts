# Distributed Work Receipts

Distributed workload cooperation changes where work runs, which organ accepts it, and how Velvet degrades or recovers when hardware is busy or unavailable.

Those decisions need evidence without turning evidence into authority.

This receipt family records events from:

```text
velvet.distributed-work-events.v1
```

and normalizes them under:

```text
velvet.receipts.distributed-work.v1
```

## Recorded events

- `NODE_ADVERTISEMENT_PUBLISHED`
- `WORK_OFFERED`
- `WORK_ACCEPTED`
- `WORK_REFUSED`
- `WORK_HANDOFF_REQUESTED`
- `WORK_COMPLETED`
- `WORK_DEGRADED`
- `WORK_RECOVERY_REASSIGNED`

## Evidence law

> Runtime places and leases. Court authorizes. Executors perform. Receipts prove what was reported.

Every accepted envelope must preserve the Event Protocol boundary:

```text
transport_only: true
canonical: false
authority: none
grants_authority: false
grants_execution: false
grants_actuation: false
```

The receipt builder rejects nested authority-bearing fields such as capability tokens, Court tokens, executor names, commands, shell requests, and hardware targets.

## Subject binding

A node-advertisement receipt must use the advertised `node_id` as its `subject_id`.

A workload receipt must use the `work_id` as its `subject_id`.

This prevents unrelated evidence from being quietly attached to another node or workload.

## Workload leases

`WORK_ACCEPTED` and `WORK_RECOVERY_REASSIGNED` receipts may preserve:

- Runtime workload lease ID;
- selected node and organ;
- placement mode;
- lease expiry;
- whether Court authorization is required.

The receipt and workload lease remain non-authoritative:

```text
handoff_transfers_no_authority: true
court_remains_independent: true
executor_contract_remains_independent: true
receipt_is_evidence_not_authority: true
```

A replacement organ must independently satisfy Runtime, Court, safety, and executor requirements. The old organ's permission never rides along with the work.

## Degradation evidence

`WORK_DEGRADED` preserves one named condition:

```text
full_replacement
partial_replacement
observe_only
capability_unavailable
```

The evidence should preserve the known loss, remaining capability, and fallback options. A failed specialist should remove only its capability where possible, not rewrite the whole body as failed.

## Important results

Completion evidence preserves:

```text
important_result
escalate_to_queen
```

This supports whole-body awareness while keeping the specialist responsible for its bounded result and the Queen responsible for final coordination.

## Receipts versus Riven

Ordinary short-lived load balancing is operational evidence, not identity lineage.

Receipts may record every placement, refusal, handoff, and recovery required by policy. Riven should preserve only durable body changes such as:

- a node formally joining or leaving the body;
- a named organ moving permanently to replacement hardware;
- a successor node assuming a continuing identity;
- a durable capability reassignment that changes the body registry.

Temporary overflow and short-lived duty absorption remain receipted operational history unless a later durable transition is explicitly approved.

## Current boundary

This receipt family does not create a network listener, scheduler, executor, capability token, Court decision, CAN transmission, actuator path, or physical authority.

Current physical authority remains **none**.
