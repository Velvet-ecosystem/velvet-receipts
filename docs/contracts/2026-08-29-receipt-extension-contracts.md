# Receipt extension contracts

Date: 2026-08-29
Status: contract draft
Owner repo: velvet-receipts

## Purpose

Receipts should prove not only that something happened, but what evidence, cost, authority, identity, and recovery conditions surrounded it. These contracts extend the receipt doctrine to newer Velvet integration ideas.

## 1. Inference Cost Receipt

Model work should leave a measurable trail.

Required fields:

```yaml
receipt_type: inference_cost
capability_requested: string
model_provider: string
model_name_or_local_id: string
execution_location: string
processor_class: cpu | gpu | npu | dsp | fpga | memory_side | unknown
input_units: integer | null
output_units: integer | null
cache_hit: boolean | null
runtime_ms: integer
estimated_energy_j: number | null
estimated_heat_class: low | medium | high | unknown
memory_peak_mb: integer | null
fallback_invoked: boolean
fallback_reason: string | null
larger_model_reason: string | null
authority_level: advise | propose | classify | none
```

Rule: AI cost belongs in the body log, not in vibes.

## 2. Event Evidence Receipt

Capture bounded evidence around anomalies.

Required fields:

```yaml
receipt_type: event_evidence
trigger_condition: string
trigger_confidence: number
pre_buffer_ms: integer
post_buffer_ms: integer
raw_sources_retained: [string]
derived_state_retained: [string]
reason_captured: string
storage_budget_bytes: integer | null
privacy_class: public | internal | private | sensitive
capture_result: complete | partial | failed
```

Use for:

- intermittent CAN glitches
- camera stalls
- presence disagreements
- power transients
- retry storms
- health trend spikes

## 3. Credential Lifecycle Receipt

Credentials should be handled as lifecycle objects.

States:

```text
detected -> blocked_or_committed -> owner_identified -> revoked -> replacement_issued -> affected_modules_checked
```

Required fields:

```yaml
receipt_type: credential_lifecycle
credential_class: api_key | oauth_token | ssh_key | pat | app_token | unknown
detected_at: string
blocked_before_commit: boolean
owner: string | null
permitted_caller: string | null
permitted_destination: string | null
expiry: string | null
revoked_at: string | null
replacement_issued: boolean
affected_modules_checked: [string]
blast_radius_class: single_token | token_class | module | node | everything
```

## 4. Credential Destination Policy Receipt

A secret should declare where it is allowed to go.

Canonical rule:

```text
secret -> permitted caller -> permitted destination -> expiry -> receipt
```

Suggested fields:

```yaml
secret_id: string
permitted_callers: [string]
permitted_destinations: [string]
plaintext_egress_allowed: boolean
fail_closed_on_destination_mismatch: boolean
last_destination_check: string
receipt_on_denial: boolean
```

## 5. Node Commissioning Receipt

Every physical organ gets a birth certificate before joining the body.

Canonical chain:

```text
hardware identity -> provisioning fixture -> firmware -> keys -> electrical test -> network test -> health baseline -> authority assignment -> installation receipt
```

Required fields:

```yaml
receipt_type: node_commissioning
node_id: string
hardware_model: string
hardware_revision: string | null
firmware_version: string
firmware_hash: string
keys_installed: boolean
electrical_test_result: pass | fail | skipped
network_test_result: pass | fail | skipped
health_baseline_id: string | null
authority_assigned: [string]
installed_location: string | null
commissioned_by: string
commissioned_at: string
```

## 6. Promotion Evidence Receipt Link

Module promotion should link to evidence, not merely a passing test.

Fields:

```yaml
receipt_type: promotion_evidence
module_name: string
module_version: string
requirement_links: [string]
architecture_reference: string
interface_contract_reference: string
test_receipt_ids: [string]
authority_analysis: string
safety_assumptions: [string]
unresolved_risks: [string]
promotion_decision: promoted | rejected | deferred
```

## 7. Vulnerability Outcome Receipt

A security issue may be fixed, mitigated, or accepted. Those are different truths.

Outcomes:

```text
fixed
mitigated
accepted
```

For `mitigated`, record:

```yaml
vulnerability_still_present: boolean
compensating_control: string
control_owner: string
control_test: string
expiry_or_review_date: string
failure_consequence: string
```

## 8. Health Trend Receipt

Trend changes deserve evidence.

Fields:

```yaml
receipt_type: health_trend
module_id: string
trend_window_hours: integer
current_faults: integer
new_faults: integer
resolved_faults: integer
recurring_faults: integer
net_direction: improving | stable | worsening | unknown
recurring_offender: boolean
reason: string | null
```

## 9. Power-Loss Transaction Receipt

When power disappears, the log should say what survived.

Fields:

```yaml
receipt_type: power_loss_transaction
node_id: string
reserve_window_ms: integer | null
noncritical_work_stopped: boolean
receipts_flushed: boolean
state_flushed: boolean
unfinished_operations_marked: [string]
storage_unmounted_cleanly: boolean
shutdown_completed_before_reserve_expired: boolean
recovery_required: boolean
```

## 10. Telemetry Reconciliation Receipt

Contradictory measurements are evidence.

Fields:

```yaml
receipt_type: telemetry_reconciliation
reconciliation_id: string
expected_relation: string
left_measurement: string
right_measurement: string
observed_left: any
observed_right: any
tolerance: any
contradiction_detected: boolean
likely_fault_domain: sensor | transport | storage | clock | software | unknown
confidence: number
```

## 11. Delegated Work Receipt

If an AI or agent is delegated work, provenance must survive.

Fields:

```yaml
receipt_type: delegated_work
human_request: string
interpreted_task: string
agent_or_provider: string
repo: string
proposed_changes: [string]
tests_run: [string]
reviewer: string | null
merge_authority: string | null
final_state: proposed | rejected | merged | abandoned
```

## Non-goals

- Receipts do not grant authority.
- Receipts do not make unsafe work safe.
- Receipts should record truth even when the truth is partial, failed, or embarrassing.
