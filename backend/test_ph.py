from controllers.ph_controller import PHController
import asyncio

# Test 1: pH status
doc = {"ph": 5.2, "created_at": "now"}

print("\n--- STATUS TEST ---")
status = PHController.evaluate_status(doc)
print(status)

# Test 2: correction plan
history = [
    {"ph": 5.8},
    {"ph": 5.5},
    {"ph": 5.2}
]

print("\n--- CORRECTION TEST ---")
correction = asyncio.run(PHController.correction_plan(history))
print(correction)