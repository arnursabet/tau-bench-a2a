"""
Demo script for τ-Bench PM domain evaluation.
Runs assessments and reports metrics.
"""

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from service.green_agent.runner import run_assessment


def main():
    print("=" * 60)
    print("τ-Bench PM Domain Demo")
    print("=" * 60)
    print()
    
    # Run 1: Simple baseline
    print("Running Assessment 1: Basic eval (1 trial)")
    print("-" * 60)
    result1 = run_assessment(
        agent_strategy="tool-calling",
        num_trials=1,
    )
    print(f"Run ID: {result1['run_id']}")
    print(f"Pass^1: {result1['pass_1']:.2%}")
    print(f"Pass^k: {result1['pass_k']}")
    print()
    
    # Run 2: Multi-trial
    print("Running Assessment 2: Multi-trial eval (3 trials)")
    print("-" * 60)
    result2 = run_assessment(
        agent_strategy="tool-calling",
        num_trials=3,
    )
    print(f"Run ID: {result2['run_id']}")
    print(f"Pass^1: {result2['pass_1']:.2%}")
    print(f"Pass^k:")
    for k, score in result2['pass_k'].items():
        print(f"  pass^{k} = {score:.2%}")
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Runs completed: 2")
    print(f"Total tasks: {result2['per_task'].__len__()}")
    print(f"Avg Pass^1 across runs: {(result1['pass_1'] + result2['pass_1']) / 2:.2%}")
    print()
    
    # Save results to JSON
    output_file = Path(__file__).parent.parent / "demo_results.json"
    results = {
        "runs": [
            {
                "id": result1["run_id"],
                "trials": 1,
                "pass_1": result1["pass_1"],
                "pass_k": result1["pass_k"],
            },
            {
                "id": result2["run_id"],
                "trials": 3,
                "pass_1": result2["pass_1"],
                "pass_k": result2["pass_k"],
            },
        ]
    }
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
