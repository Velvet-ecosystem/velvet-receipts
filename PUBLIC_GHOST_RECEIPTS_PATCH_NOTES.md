# Public Ghost Receipts Patch Notes

This patch adds receipt support for the public Velvet ghost CAN demo.

## Added

- `ghost_can_receipts.py`
  - Builds canonical receipts for `vehicle.can.ghost_observation`.
  - Rejects unsafe evidence flags.
  - Records observation-only constraints.
- `tests/test_ghost_can_receipts.py`
  - Verifies safe receipt construction.
  - Verifies unsafe flags are rejected.
  - Verifies the Runtime receipt router accepts ghost CAN events.
- `examples/ghost_can_receipt.py`
  - Builds, logs, and prints a finalized ghost CAN receipt.
- `docs/ghost_can_receipt_contract.md`
  - Documents the event, required flags, and receipt meaning.

## Updated

- `runtime_receipts.py`
  - Routes `vehicle.can.ghost_observation` to the stricter ghost CAN receipt constructor.
- `velvet_receipts/__init__.py`
  - Exposes the ghost CAN receipt helpers.
- `pyproject.toml`
  - Includes runtime, memory, and ghost receipt modules in package builds.
- `README.md`
  - Documents public ghost CAN receipt support.

## Safety posture

This patch does not add CAN authority, physical bus access, frame transmission, or vehicle actuation. It only records a verified synthetic/read-only ghost observation in the append-only receipt chain.
