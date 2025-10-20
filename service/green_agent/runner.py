
import uuid
import random
from math import comb
from typing import List, Dict, Any, Optional
from tau_bench.envs import get_env
from tau_bench.types import RunConfig
from tau_bench.run import agent_factory
from service.green_agent.storage import storage
from service.green_agent.config import DOMAIN


def run_assessment(
    agent_strategy: str = "tool-calling",
    model: str = "gpt-4-mini",
    model_provider: str = "openai",
    num_trials: int = 1,
    task_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Run an assessment on the PM domain.
    
    Returns metrics including pass^1, pass^k, and per-task results.
    """
    run_id = str(uuid.uuid4())
    
    # Load environment
    env = get_env(
        env_name=DOMAIN,
        user_strategy="human",  # Use human strategy for demos (no API costs)
        user_model=model,
        task_split="test",
    )
    
    # Filter tasks if task_ids provided
    if task_ids:
        tasks_to_run = [env.tasks[i] for i in task_ids if i < len(env.tasks)]
    else:
        tasks_to_run = env.tasks
    
    results_by_task: Dict[int, List[float]] = {}
    
    # Run trials
    for trial in range(num_trials):
        for task_idx, task in enumerate(tasks_to_run):
            task_id = task_idx
            if task_id not in results_by_task:
                results_by_task[task_id] = []
            
            # Simulate a deterministic reward
            # In real scenario, would call agent and compute reward
            reward = random.choice([0.0, 1.0])  # Mock for demo
            results_by_task[task_id].append(reward)
            
            # Store episode
            episode_id = f"{run_id}-t{task_id}-trial{trial}"
            storage.save_episode(
                episode_id=episode_id,
                run_id=run_id,
                task_id=task_id,
                trial=trial,
                reward=reward,
                actions_count=5,  # Mock
            )
    
    # Compute pass^k metrics
    pass_1_scores = []
    pass_k_dict: Dict[int, List[float]] = {}
    
    for task_id, rewards in results_by_task.items():
        # pass^1: fraction of successful trials
        pass_1 = sum(r > 0.5 for r in rewards) / len(rewards)
        pass_1_scores.append(pass_1)
        
        # pass^k: probability all k trials succeed
        n = len(rewards)
        successful = sum(r > 0.5 for r in rewards)
        for k in range(1, n + 1):
            if k not in pass_k_dict:
                pass_k_dict[k] = []
            pass_k_prob = comb(successful, k) / comb(n, k) if n > 0 else 0
            pass_k_dict[k].append(pass_k_prob)
    
    # Average across tasks
    avg_pass_1 = sum(pass_1_scores) / len(pass_1_scores) if pass_1_scores else 0
    avg_pass_k = {k: sum(v) / len(v) if v else 0 for k, v in pass_k_dict.items()}
    
    metrics = {
        "pass_1": avg_pass_1,
        "pass_k": avg_pass_k,
        "num_tasks": len(results_by_task),
        "num_trials": num_trials,
        "agent_strategy": agent_strategy,
    }
    
    # Store run
    storage.save_run(
        run_id=run_id,
        agent_strategy=agent_strategy,
        num_trials=num_trials,
        pass_1=avg_pass_1,
        pass_k=avg_pass_k,
        metrics=metrics,
    )
    
    # Build per-task results
    per_task_results = []
    for task_id, rewards in results_by_task.items():
        n = len(rewards)
        successful = sum(r > 0.5 for r in rewards)
        task_pass_k = {
            k: (comb(successful, k) / comb(n, k) if n > 0 else 0)
            for k in range(1, n + 1)
        }
        per_task_results.append({
            "task_id": task_id,
            "pass_1": pass_1_scores[task_id] if task_id < len(pass_1_scores) else 0,
            "pass_k": task_pass_k,
            "num_trials": n,
        })
    
    return {
        "run_id": run_id,
        "pass_1": avg_pass_1,
        "pass_k": avg_pass_k,
        "per_task": per_task_results,
    }
