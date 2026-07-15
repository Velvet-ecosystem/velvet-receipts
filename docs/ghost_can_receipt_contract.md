# Ghost CAN Receipt Contract

`velvet-receipts` can record the public ghost-system CAN observation emitted by `velvet-runtime` without turning that observation into authority.

The supported event is:

```text
vehicle.can.ghost_observation
```

This is the receipt-side ledger tooth for the jarred-car demo:

```text
synthetic CAN fixture
-> velvet-vehicle-can read-only ghost observation
-> velvet-runtime Court/gate/executor path
-> velvet-receipts ghost CAN receipt
-> append-only hash chain
```

## Required safety flags

A ghost CAN receipt is accepted only when the payload says all of the following:

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

If any of those values are missing or unsafe, receipt construction fails.

## What the receipt means

A ghost CAN receipt means Velvet recorded a synthetic/read-only vehicle observation. It does not mean the system opened a physical CAN bus, transmitted a frame, moved an actuator, or gained vehicle authority.

The canonical receipt uses:

```text
event: vehicle.can.ghost_observation
decision: record_observation
policy: PublicGhostCanReceiptContract
authorized_by: RuntimeReadOnlyPath
domain: vehicle-can-ghost
```

## Example

```bash
python examples/ghost_can_receipt.py
```

The example writes `ghost_can_receipts.log` and prints the finalized receipt JSON.
