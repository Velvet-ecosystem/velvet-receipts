Receipt Chain Contract

This repo defines Velvet's receipt records, continuity links, integrity checks, and audit trail.

The canonical doctrine lives in:

- "velvet-ai-core/docs/boot_identity_sequence.md"
- "velvet-ai-core/docs/naming_and_binding.md"
- "velvet-ai-core/docs/retrofit_body_registry.md"
- "velvet-ai-core/docs/room_body_interface.md"
- "velvet-ai-core/docs/scene_doctrine.md"

This document defines the receipt repo's local contract.

Receipts record meaningful system decisions and actions.

A receipt is evidence that a transition passed through the required identity, policy, safety, and execution boundaries.

A receipt does not retroactively authorize an action.

Authorization happens before execution.

The receipt records what happened afterward.

Receipt Responsibilities

The receipt layer may:

- record boot identity results
- record authorization decisions
- record body registry changes
- record naming and binding changes
- record protected scene access
- record degraded-state transitions
- record executor results
- preserve lineage across restarts and migrations
- link records through previous hashes
- detect missing or altered receipt history
- support verification and audit tools

The receipt layer may not:

- authorize actions by itself
- replace identity verification
- replace capability checks
- replace safety gates
- fabricate successful execution
- silently rewrite historical records
- erase retired body history
- treat an unsigned or invalid record as trusted
- accept protected actions without a valid receipt policy

Receipt Timing

Protected actions should produce receipts after execution or after a final decision.

Recommended flow:

intent or request
  -> identity / context check
  -> policy authorization
  -> capability token check
  -> safety gate
  -> executor
  -> result
  -> receipt

Denied actions may also produce receipts when the denial is security-relevant, safety-relevant, or useful for diagnosing repeated failures.

Receipt Types

Suggested receipt types:

boot_identity
authorization_granted
authorization_denied
actuation_result
body_registered
body_updated
body_retired
binding_created
binding_updated
binding_removed
degraded_state_entered
degraded_state_cleared
protected_scene_access
capability_policy_changed
executor_failure
emergency_action
migration
restore
continuity_checkpoint

Minimum Receipt Fields

A receipt should include enough information to verify the event without exposing unnecessary secrets.

Suggested fields:

receipt_id
receipt_type
timestamp
instance_id
surface_id
body_id
profile_context
source
intent_reference
authorization_result
executor
result
degraded_state
previous_hash
hash
signature_status
doctrine_version
system_version

Sensitive credentials, private phrases, raw keys, and unnecessary personal information should not be stored in plaintext.

Integrity Chain

Receipts should be linked so alteration or deletion becomes detectable.

Recommended relationship:

previous receipt hash
  -> current receipt contents
  -> current receipt hash
  -> optional local integrity tag or signature

A broken chain should trigger verification failure, degraded trust, or protected mode.

A broken chain must not be silently ignored.

No Valid Receipt, No Protected Actuation

For protected actions, Velvet's enforcement doctrine is:

no valid receipt path = deny protected actuation

This does not mean a receipt grants authority.

It means the system must be capable of producing and preserving a valid receipt for the authorized action.

If the receipt system is unavailable, protected actions should fail closed unless an explicit emergency policy defines otherwise.

Boot Receipts

Boot identity should create a receipt describing:

- active system version
- doctrine version
- instance identity
- surface identity
- body identity
- body fingerprint status
- active profile context
- receipt ledger status
- degraded organs
- blocked capabilities
- continuity chain status

Boot receipts establish the starting point for each runtime session.

Registry and Binding Receipts

Changes to body registry records, names, profiles, authority bindings, and capability policy should create receipts.

A change receipt should preserve:

old value or old record reference
new value or new record reference
authorized by
reason
body context
surface context
timestamp
receipt chain reference

Executor Receipts

Executor receipts should record the requested action and actual result separately.

Example:

requested_action: lock_driver_door
authorization_result: granted
executor_result: success
observed_final_state: locked

A granted request with a failed executor result must not be recorded as successful actuation.

Verification

Receipt verification should check:

- required fields are present
- hashes match receipt contents
- previous-hash linkage is intact
- signatures or integrity tags are valid where required
- receipt type matches the recorded action
- timestamps are plausible
- body and surface references are known
- authorization and executor results are not conflated
- protected actions have the required receipt trail

Retention

Receipts may be archived, compacted, or checkpointed according to local policy.

Compaction must not erase continuity proof.

Historical body records, binding changes, emergency actions, and protected actuator records should remain verifiable after archival.

Public Rule

Identity is checked.

Policy decides.

Gates enforce.

Executors act.

Receipts prove what occurred.