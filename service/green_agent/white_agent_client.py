
import asyncio
import json
from typing import Dict, Any, List, Optional
import httpx
from service.green_agent.a2a_schemas import A2ARequest, A2AResponse, TaskInput, TaskOutput


class WhiteAgentClient:
    """HTTP client to communicate with A2A-compliant white agents."""
    
    def __init__(self, agent_url: str, timeout: float = 30.0):
        """Initialize client for a white agent.
        
        Args:
            agent_url: Base URL of the white agent (e.g., http://localhost:8001)
            timeout: HTTP request timeout in seconds
        """
        self.agent_url = agent_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get_agent_card(self) -> Dict[str, Any]:
        """Fetch the white agent's capabilities."""
        try:
            response = await self.client.get(f"{self.agent_url}/a2a/agent-card")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch agent card from {self.agent_url}: {e}")
    
    async def reset_agent(self) -> bool:
        """Reset the white agent state."""
        try:
            request = A2ARequest(
                method="agent/reset",
                params={},
                id="reset_1"
            )
            response = await self.client.post(
                f"{self.agent_url}/a2a/reset",
                json=request.model_dump()
            )
            response.raise_for_status()
            return response.json().get("status") == "ok"
        except Exception as e:
            print(f"Warning: Reset failed for {self.agent_url}: {e}")
            return False
    
    async def execute_task(
        self,
        task_input: TaskInput,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a task on the white agent.
        
        Args:
            task_input: Task to execute
            context: Optional execution context
        
        Returns:
            Agent response with tool calls or error
        """
        try:
            request = A2ARequest(
                method="tasks/execute",
                params={
                    "task_id": task_input.task_id,
                    "instruction": task_input.instruction,
                    "tools": task_input.tools,
                    "environment_state": task_input.environment_state,
                    "context": context or {},
                },
                id=f"task_{task_input.task_id}"
            )
            
            response = await self.client.post(
                f"{self.agent_url}/a2a/execute_task",
                json=request.model_dump()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "task_id": task_input.task_id,
            }
    
    async def get_result(self, result_id: str) -> Dict[str, Any]:
        """Fetch a previous task result."""
        try:
            response = await self.client.get(f"{self.agent_url}/a2a/result/{result_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch result {result_id}: {e}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class WhiteAgentEvaluator:
    """Evaluates responses from white agents against PM domain requirements."""
    
    def __init__(self, env):
        """Initialize evaluator with PM environment.
        
        Args:
            env: τ-Bench PM environment with tools and evaluation logic
        """
        self.env = env
    
    def extract_tool_calls(self, agent_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from white agent response.
        
        Expected format:
        {
            "result": {
                "actions": [
                    {"name": "tool_name", "kwargs": {...}},
                    ...
                ],
                "messages": [...]
            }
        }
        """
        try:
            result = agent_response.get("result", {})
            actions = result.get("actions", [])
            return actions
        except Exception as e:
            print(f"Warning: Failed to extract actions from response: {e}")
            return []
    
    async def evaluate_response(
        self,
        task_input: TaskInput,
        agent_response: Dict[str, Any],
        ground_truth_actions: List[Dict[str, Any]],
        ground_truth_outputs: List[str],
    ) -> Dict[str, Any]:
        """Evaluate agent response against ground truth.
        
        Args:
            task_input: Original task
            agent_response: Agent's response
            ground_truth_actions: Expected tool calls
            ground_truth_outputs: Expected outputs in responses
        
        Returns:
            Evaluation result with reward and metadata
        """
        reward = 0.0
        violations = 0
        
        # Check for errors
        if "error" in agent_response:
            return {
                "task_id": task_input.task_id,
                "reward": 0.0,
                "status": "error",
                "error": agent_response["error"],
                "violations": violations,
            }
        
        # Extract tool calls
        actions = self.extract_tool_calls(agent_response)
        
        # Verify ground truth actions were executed
        # (simplified: check if expected actions appear in response)
        expected_action_names = [a.get("name") for a in ground_truth_actions]
        actual_action_names = [a.get("name") for a in actions]
        
        actions_match = set(expected_action_names) == set(actual_action_names)
        
        if not actions_match:
            violations += 1
        
        # Verify outputs
        response_text = json.dumps(agent_response)
        outputs_found = sum(1 for out in ground_truth_outputs if out.lower() in response_text.lower())
        
        if outputs_found == len(ground_truth_outputs):
            outputs_match = True
        else:
            outputs_match = False
            violations += 1
        
        # Compute reward
        reward = 1.0 if (actions_match and outputs_match) else 0.0
        
        return {
            "task_id": task_input.task_id,
            "reward": reward,
            "status": "completed",
            "actions_match": actions_match,
            "outputs_match": outputs_match,
            "violations": violations,
            "expected_actions": expected_action_names,
            "actual_actions": actual_action_names,
        }
