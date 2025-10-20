
from fastapi import FastAPI, HTTPException
from datetime import datetime
import json
from typing import Dict, Any
from service.green_agent.a2a_schemas import (
    AgentCard, AgentCapabilities, AgentEndpoints,
    AssessmentRequest, AssessmentResult, TaskMetrics,
    AgentRegistration, RegistrationResponse, TaskInput
)
from service.green_agent.config import SERVICE_NAME, SERVICE_VERSION, DOMAIN, METRICS
from service.green_agent.storage import storage

app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION)

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
def execute_task(request: Dict[str, Any]) -> dict:
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
        evaluation = {
            "task_id": task_id,
            "reward": 0.5,  # Mock reward
            "status": "completed",
            "actions_match": True,
            "outputs_match": False,
            "violations": 0,
            "expected_actions": ["list_tickets"],
            "actual_actions": ["list_tickets"],
            "note": "Demo mock evaluation - not yet calling white agent",
        }
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "task_id": task_id,
                "assessment_id": assessment_id,
                "evaluation": evaluation,
            },
            "id": request.get("id", "1"),
        }
            
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -1, "message": str(e)},
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
