# examples/basic_usage.py
# Velvet Receipts — Basic Usage Example
# GPLv3 — aligned with Velvet core infrastructure

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from receipt import Receipt
from receipt_logger import ReceiptLogger

LOG_FILE = "receipts_example.log"

# Start fresh for this demo
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

logger = ReceiptLogger(filepath=LOG_FILE)

# ------------------------------------------------------------------
# Receipt 1: System detects low light and engages headlights
# ------------------------------------------------------------------
r1 = Receipt(
    event="low_light_detected",
    decision="turn_on_headlights",
    result="headlights_on",
    policy="AutoHeadlightPolicy",
    authorized_by="Core",
    context={"ambient_light_lux": 12},
    constraints={"speed_kmh": "<= 120", "manual_override": False},
    domain="lighting",
    confidence=0.97,
)

logger.log(r1)
print(f"[1] Logged: {r1.event}")
print(f"    hash:          {r1.hash[:20]}...")
print(f"    previous_hash: {r1.previous_hash}")

# ------------------------------------------------------------------
# Receipt 2: Driver overrides; system yields and records authority
# ------------------------------------------------------------------
r2 = Receipt(
    event="driver_override",
    decision="defer_to_manual_control",
    result="headlights_manual",
    policy="DriverSovereigntyPolicy",
    authorized_by="Core",
    context={"override_source": "steering_column_stalk"},
    constraints={"manual_override": True},
    domain="lighting",
    notes="Driver assumes direct control. AutoHeadlightPolicy suspended.",
)

logger.log(r2)
print(f"\n[2] Logged: {r2.event}")
print(f"    hash:          {r2.hash[:20]}...")
print(f"    previous_hash: {r2.previous_hash[:20]}...")
print(f"    chains to r1:  {r2.previous_hash == r1.hash}")

# ------------------------------------------------------------------
# Chain verification
# ------------------------------------------------------------------
print("\n--- Verifying chain ---")
valid, errors = logger.verify_chain()

if valid:
    print("Chain intact. All receipts verified.")
else:
    print("Chain FAILED. Integrity errors:")
    for e in errors:
        print(f"  ! {e}")
