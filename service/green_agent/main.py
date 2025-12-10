from dotenv import load_dotenv
from service.green_agent.mock_white_agent_simulator import MockWhiteAgentSimulator
from service.green_agent.white_agent_client import WhiteAgentClient, WhiteAgentEvaluator
from service.green_agent.config import DOMAIN
from tau_bench.envs import get_env
import asyncio
import os
from fastapi import FastAPI, HTTPException
from datetime import datetime
import json
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()
from service.green_agent.a2a_schemas import (
    AgentCard, AgentCapabilities, AgentEndpoints,
    AssessmentRequest, AssessmentResult, TaskMetrics,
    AgentRegistration, RegistrationResponse, TaskInput
)
from service.green_agent.config import SERVICE_NAME, SERVICE_VERSION, DOMAIN, METRICS
from service.green_agent.storage import storage

app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION)

# Choose execution mode: mock or real
USE_MOCK = os.getenv("USE_MOCK_WHITE_AGENT", "false").lower() == "true"
mock_simulator = MockWhiteAgentSimulator(success_rate=0.7) if USE_MOCK else None

if USE_MOCK:
    print("[GREEN AGENT] using MockWhiteAgentSimulator")
else:
    print("[GREEN AGENT] using actual white agents")

# Store registered white agents
registered_agents: Dict[str, Dict] = {}


def get_agent_card() -> AgentCard:
    """Generate A2A Agent Card for the green agent."""
    return AgentCard(
        name="τ-PM Green Agent",
        description="Evaluates tool-use agents on project management tasks via τ-Bench PM domain",
        version=SERVICE_VERSION,
        protocol="a2a",
        capabilities=AgentCapabilities(
            domains=["project-management"],
            metrics=METRICS,
            max_agents=10,
            max_trials=5,
        ),
        endpoints=AgentEndpoints(
            agent_card="GET /a2a/agent-card",
            reset="POST /a2a/reset",
            execute_task="POST /a2a/execute_task",
            get_result="GET /a2a/result/{assessment_id}",
            register_agent="POST /a2a/register_agent",
        ),
        authentication="bearer_token",
    )


# ============================================================================
# Health & Discovery
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/a2a/agent-card")
def fetch_agent_card() -> dict:
    """A2A: Return green agent's capabilities and endpoints."""
    card = get_agent_card()
    return card.model_dump()

@app.get("/.well-known/agent-card.json")
def well_known_agent_card() -> dict:
    """A2A Standard Discovery Endpoint for AgentBeats."""
    card = get_agent_card()
    return card.model_dump()


# ============================================================================
# A2A Assessment Endpoints
# ============================================================================

@app.post("/a2a/register_agent")
def register_white_agent(registration: AgentRegistration) -> RegistrationResponse:
    """A2A: Register a white agent for evaluation.
    
    White agents submit their URL and optionally their agent card.
    """
    try:
        assessment_id = f"assess_{len(registered_agents) + 1}"
        registered_agents[assessment_id] = {
            "agent_url": registration.agent_url,
            "agent_card": registration.agent_card,
            "submission_time": datetime.now().isoformat(),
            "status": "registered",
        }
        
        return RegistrationResponse(
            status="accepted",
            assessment_id=assessment_id,
            message=f"Agent registered for assessment {assessment_id}",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/a2a/reset")
def reset_green_agent():
    """A2A: Reset the green agent state (idempotent)."""
    return {"status": "ok", "message": "Green agent reset"}


@app.post("/a2a/execute_task")
async def execute_task(request: Dict[str, Any]) -> dict:
    """A2A: Execute a task on registered white agents.
    
    Receives task definition and orchestrates evaluation across white agents.
    For demo purposes, this returns a mock evaluation.
    """
    try:
        params = request.get("params", {})
        assessment_id = params.get("assessment_id")
        task_id = params.get("task_id", "0")
        instruction = params.get("instruction", "")
        tools = params.get("tools", [])
        
        if not assessment_id:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Missing assessment_id"},
                "id": request.get("id", "1"),
            }
        
        if assessment_id not in registered_agents:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32001, "message": f"Assessment {assessment_id} not found"},
                "id": request.get("id", "1"),
            }
        
        # For demo: return a mock evaluation
        # In production: would call WhiteAgentClient to execute on white agent
        print(f"\n{'='*60}")
        print(f"GREEN AGENT: Starting assessment {assessment_id}, task {task_id}")
        print(f"{'='*60}")
        
        print("[GREEN AGENT] Preparing environment")
        
        task_idx = int(task_id) if str(task_id).isdigit() else 0
        
        try:
            env = get_env(
                env_name=DOMAIN,
                user_strategy="human",  # for demo
                user_model="dummy",  
                task_split="test",
                task_index=task_idx,
            )
            print(f"[GREEN AGENT] Loaded {len(env.tasks)} tasks")
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32001, "message": f"Failed to load environment: {str(e)}"},
                "id": request.get("id", "1"),
            }
        
        if task_idx >= len(env.tasks):
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": f"Task {task_id} not found"},
                "id": request.get("id", "1"),
            }
        
        task = env.tasks[task_idx]
        task_tools = tools if tools else env.tools_info
        task_instruction = instruction if instruction else getattr(task, 'instruction', 'Complete task')
        
        print(f"[GREEN AGENT] Task instruction: {task_instruction[:100]}...")
        print(f"[GREEN AGENT] Available tools: {len(task_tools)}")
        
        # Choose execution mode
        if USE_MOCK:
            print("[GREEN AGENT] Using mock simulator")
            # Reset white agent before task
            print("[GREEN AGENT] Resetting white agent")
            reset_success = await mock_simulator.reset()
            if not reset_success:
                print("[GREEN AGENT] Reset failed")
            else:
                print("[GREEN AGENT] Reset successful")
            
            # Distribute task to white agent
            print("[GREEN AGENT] Distributing task to white agent")
            agent_response = await mock_simulator.execute_task(
                task_id=str(task_id),
                instruction=task_instruction,
                tools=task_tools
            )
            print("[GREEN AGENT] Received response from white agent")
        else:
            print("[GREEN AGENT] Using real white agent client")
            agent_info = registered_agents[assessment_id]
            agent_url = agent_info["agent_url"]
            
            # Initialize white agent client
            client = WhiteAgentClient(agent_url, timeout=60.0)
            
            try:
                # Reset white agent before task
                print(f"[GREEN AGENT] Resetting white agent at {agent_url}")
                reset_success = await client.reset_agent()
                if not reset_success:
                    print("[GREEN AGENT] Reset failed")
                else:
                    print("[GREEN AGENT] Reset successful")
                
                # Prepare task input
                task_input = TaskInput(
                    task_id=str(task_id),
                    instruction=task_instruction,
                    tools=task_tools,
                    environment_state=None,
                )
                
                # Distribute task to white agent
                print("[GREEN AGENT] Distributing task to white agent")
                agent_response = await client.execute_task(task_input)
                print("[GREEN AGENT] Received response from white agent")
                
                await client.close()
                
            except Exception as e:
                print(f"[GREEN AGENT] Error communicating with white agent: {e}")
                await client.close()
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000,
                        "message": f"Failed to communicate with white agent: {str(e)}"
                    },
                    "id": request.get("id", "1"),
                }
        
        # Verify environment / Evaluate response
        print("[GREEN AGENT] Evaluating white agent response")
        evaluator = WhiteAgentEvaluator(env)
        
        task_input = TaskInput(
            task_id=str(task_id),
            instruction=task_instruction,
            tools=task_tools,
            environment_state=None,
        )
        
        ground_truth_actions = getattr(task, 'expected_actions', [])
        ground_truth_outputs = getattr(task, 'expected_outputs', [])
        
        evaluation = await evaluator.evaluate_response(
            task_input=task_input,
            agent_response=agent_response,
            ground_truth_actions=ground_truth_actions,
            ground_truth_outputs=ground_truth_outputs,
        )
        
        print(f"[GREEN AGENT] Evaluation complete:")
        print(f"[GREEN AGENT] Reward: {evaluation.get('reward', 0.0)}")
        print(f"[GREEN AGENT] Status: {evaluation.get('status', 'unknown')}")
        print(f"[GREEN AGENT] Violations: {evaluation.get('violations', 0)}")
        
        # Report metrics
        print("[GREEN AGENT] Reporting results")
        result = {
            "jsonrpc": "2.0",
            "result": {
                "task_id": str(task_id),
                "assessment_id": assessment_id,
                "evaluation": evaluation,
                "timestamp": datetime.now().isoformat(),
                "mode": "mock_simulator" if USE_MOCK else "real_white_agent",
            },
            "id": request.get("id", "1"),
        }
        
        return result
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "jsonrpc": "2.0",
            "error": {"code": -1, "message": f"Internal error: {str(e)}"},
            "id": request.get("id", "1"),
        }


@app.get("/a2a/result/{assessment_id}")
def get_assessment_result(assessment_id: str):
    """A2A: Retrieve assessment results."""
    if assessment_id not in registered_agents:
        raise HTTPException(status_code=404, detail=f"Assessment {assessment_id} not found")
    
    agent_info = registered_agents[assessment_id]
    return {
        "assessment_id": assessment_id,
        "status": agent_info.get("status", "pending"),
        "agent_url": agent_info.get("agent_url"),
        "submission_time": agent_info.get("submission_time"),
    }


if __name__ == "__main__":
    import uvicorn
    import os

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8000"))
    
    print(f"Starting Green Agent on {host}:{port}")
    uvicorn.run(app, host=host, port=port)