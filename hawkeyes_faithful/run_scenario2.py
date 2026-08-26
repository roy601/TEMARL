# run_scenario2.py
import sys
import time
sys.path.insert(0, r'C:\Users\T25301092\thesis_project\hawkeyes_faithful')
from run_experiments import run_all_scenarios

print("=" * 60)
print("HAWKEYES — SCENARIO 2")
print("HMARL vs MARL comparison")
print("6 attacks x 4 configs x 10 trials x 2 methods = 480 runs")
print("Estimated time on RTX 4080: ~17-18 hours")
print("Safe to interrupt — resumes automatically")
print("=" * 60)
print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

run_all_scenarios(
    training_steps=30000,
    n_trials=10,
    n_eval=1000,
    scenarios_to_run=[2]
)

print(f"\nFinished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")