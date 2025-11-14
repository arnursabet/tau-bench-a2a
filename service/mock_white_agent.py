
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn

app = FastAPI(title="Mock White Agent", version="1.0.0")


class A2ARequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None


class AgentCard(BaseModel):
    name: str
    description: str
    version: str
    protocol: str
    capabilities: Dict[str, Any]


def get_mock_agent_card() -> dict:
    """Return a minimal A2A-compliant agent card."""
    return {
        "name": "Mock White Agent",
        "description": "A simple mock agent for testing A2A protocol",
        "version": "1.0.0",
        "protocol": "a2a",
        "capabilities": {
            "domains": ["project-management"],
            "metrics": ["pass_1", "pass_k"],
        },
    }


@app.get("/a2a/agent-card")
def fetch_agent_card() -> dict:
    """A2A: Return agent capabilities."""
    return get_mock_agent_card()


@app.post("/a2a/reset")
def reset_agent():
    """A2A: Reset agent state."""
    return {
        "jsonrpc": "2.0",
        "result": {"status": "ok"},
        "id": "1",
    }


@app.post("/a2a/execute_task")
def execute_task(request: A2ARequest) -> dict:
    """A2A: Execute a task.
    
    This mock agent returns a simple response with tool calls.
    In a real scenario, the agent would:
    1. Parse the task instruction
    2. Plan tool usage
    3. Execute tools against the environment
    4. Return results
    """
    params = request.params
    task_id = params.get("task_id", "0")
    instruction = params.get("instruction", "")
    
    # Mock response: return some tool calls
    # For demo: just echo back the instruction
    response = {
        "jsonrpc": "2.0",
        "result": {
            "task_id": task_id,
            "status": "success",
            "actions": [
                {
                    "name": "list_tickets",
                    "kwargs": {},
                }
            ],
            "message": f"Processed task: {instruction[:50]}...",
        },
        "id": request.id or "1",
    }
    
    return response


@app.get("/a2a/result/{result_id}")
def get_result(result_id: str):
    """A2A: Retrieve a previous result."""
    return {
        "jsonrpc": "2.0",
        "result": {
            "result_id": result_id,
            "status": "completed",
            "data": {},
        },
        "id": "1",
    }


if __name__ == "__main__":
    import os
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("AGENT_PORT", "8001"))
    
    print(f"Starting Mock White Agent on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
