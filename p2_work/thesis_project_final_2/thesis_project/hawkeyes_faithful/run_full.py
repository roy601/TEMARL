# run_full.py
import sys
sys.path.insert(0, r'C:\Users\T25301092\thesis_project\hawkeyes_faithful')
from run_experiments import run_all_scenarios
import time

print("=" * 60)
print("HAWKEYES FAITHFUL REPRODUCTION — FULL RUN")
print("RTX 4080 — Scenario 1 only")
print("6 attacks × 4 configs × 10 trials = 240 runs")
print("Estimated: ~10 hours")
print("Safe to interrupt — resumes automatically")
print("=" * 60)
print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

run_all_scenarios(
    training_steps=30000,
    n_trials=10,
    n_eval=1000,
    scenarios_to_run=[1]
)

print(f"\nFinished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")