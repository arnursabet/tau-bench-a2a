"""
FastAPI Service for LLM-Based White Agent
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn

from service.white_agent.llm_agent import LLMWhiteAgent

# Load environment variables from .env file
load_dotenv()


app = FastAPI(title="LLM White Agent", version="1.0.0")

# Initialize the LLM agent
# Use environment variable for model selection
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
agent = LLMWhiteAgent(model=MODEL)


class A2ARequest(BaseModel):
    """A2A protocol request format"""
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None


class AgentCard(BaseModel):
    """Agent card describing capabilities"""
    name: str
    description: str
    version: str
    protocol: str
    capabilities: Dict[str, Any]


def get_agent_card() -> dict:
    """Return A2A-compliant agent card"""
    return {
        "name": "LLM White Agent",
        "description": "An LLM-based agent that can execute project management tasks",
        "version": "1.0.0",
        "protocol": "a2a",
        "capabilities": {
            "domains": ["project-management"],
            "reasoning": "llm-based",
            "model": MODEL,
            "max_concurrent_tasks": 1,
        },
        "endpoints": {
            "agent_card": "GET /a2a/agent-card",
            "reset": "POST /a2a/reset",
            "execute_task": "POST /a2a/execute_task",
        },
        "authentication": None,
    }

"""
A2A Protocol Endpoints
"""

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "LLM White Agent", "model": MODEL}


@app.get("/a2a/agent-card")
def fetch_agent_card() -> dict:
    """A2A: Return agent capabilities"""
    return get_agent_card()


@app.get("/.well-known/agent-card.json")
def well_known_agent_card() -> dict:
    """A2A: Standard discovery endpoint"""
    return get_agent_card()


@app.post("/a2a/reset")
def reset_agent():
    """A2A: Reset agent state"""
    agent.reset()
    return {
        "jsonrpc": "2.0",
        "result": {"status": "ok", "message": "Agent reset successfully"},
        "id": "1",
    }


@app.post("/a2a/execute_task")
async def execute_task(request: A2ARequest) -> dict:
    """
    A2A: Execute a task
    """
    try:
        params = request.params
        task_id = params.get("task_id", "0")
        instruction = params.get("instruction", "")
        tools = params.get("tools", [])
        
        if not instruction:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602,
                    "message": "Missing required parameter: instruction"
                },
                "id": request.id or "1",
            }
        
        # Execute task using LLM agent
        result = await agent.execute_task(
            task_id=task_id,
            instruction=instruction,
            tools=tools
        )
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": f"Task execution failed: {str(e)}"
            },
            "id": request.id or "1",
        }


if __name__ == "__main__":
    # Read host and port from environment variables
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("AGENT_PORT", "8002"))
    
    print(f"Starting LLM White Agent on {host}:{port}")
    print(f"Model: {MODEL}")
    uvicorn.run(app, host=host, port=port)

