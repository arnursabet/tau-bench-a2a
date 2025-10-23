#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tau_bench.envs import get_env
from tau_bench.envs.pm.tasks_test import TASKS_TEST

def test_ground_truth_data_state():
    """Test what the ground truth data state should be for each task."""
    
    # Load the PM environment
    env = get_env(
        env_name="pm",
        user_strategy="mock",
        user_model="gpt-4o",
        task_split="test",
    )
    
    print("=== Testing Ground Truth Data States ===\n")
    
    for task_idx, task in enumerate(TASKS_TEST):
        print(f"Task {task_idx}: {task.instruction}")
        print(f"Expected actions: {[action.name for action in task.actions]}")
        
        # Reset environment to initial state
        env.reset(task_index=task_idx)
        initial_data_hash = env.get_data_hash()
        print(f"Initial data hash: {initial_data_hash}")
        
        # Execute ground truth actions
        for action in task.actions:
            if action.name != "respond":
                result = env.step(action)
                print(f"  {action.name}: {result.observation[:100]}...")
        
        final_data_hash = env.get_data_hash()
        print(f"Final data hash: {final_data_hash}")
        print(f"Data changed: {initial_data_hash != final_data_hash}")
        print("-" * 80)

if __name__ == "__main__":
    test_ground_truth_data_state()
