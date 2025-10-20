"""
Test A2A Protocol integration between green and white agents.

This script:
1. Starts a mock white agent on port 8001
2. Registers it with the green agent on port 8000
3. Sends a task to the white agent
4. Evaluates the response
5. Prints results
"""

import asyncio
import json
import time
import subprocess
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

import httpx
from service.green_agent.a2a_schemas import A2ARequest, AgentRegistration


async def test_a2a_integration():
    """Run integration test."""
    
    print("=" * 70)
    print("A2A Protocol Integration Test")
    print("=" * 70)
    
    # Start mock white agent
    print("\n1. Starting mock white agent on http://localhost:8001...")
    white_agent_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "service.mock_white_agent:app", "--port", "8001"],
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2)  # Give it time to start
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: Green agent advertises itself
            print("\n2. Fetching green agent card...")
            green_card = await client.get("http://localhost:8000/a2a/agent-card")
            print(f"   Status: {green_card.status_code}")
            print(f"   Card: {json.dumps(green_card.json(), indent=2)}")
            
            # Test 2: White agent advertises itself
            print("\n3. Fetching white agent card...")
            white_card = await client.get("http://localhost:8001/a2a/agent-card")
            print(f"   Status: {white_card.status_code}")
            print(f"   Card: {json.dumps(white_card.json(), indent=2)}")
            
            # Test 3: Register white agent with green agent
            print("\n4. Registering white agent with green agent...")
            registration = AgentRegistration(
                agent_url="http://localhost:8001",
                agent_card=white_card.json(),
            )
            reg_response = await client.post(
                "http://localhost:8000/a2a/register_agent",
                json=registration.model_dump(),
            )
            print(f"   Status: {reg_response.status_code}")
            reg_data = reg_response.json()
            assessment_id = reg_data.get("assessment_id")
            print(f"   Assessment ID: {assessment_id}")
            print(f"   Response: {json.dumps(reg_data, indent=2)}")
            
            # Test 4: Reset white agent
            print("\n5. Resetting white agent...")
            reset_response = await client.post(
                "http://localhost:8001/a2a/reset",
                json=A2ARequest(
                    method="agent/reset",
                    params={},
                    id="1",
                ).model_dump(),
            )
            print(f"   Status: {reset_response.status_code}")
            print(f"   Response: {json.dumps(reset_response.json(), indent=2)}")
            
            # Test 5: Send task to white agent
            print("\n6. Sending task to white agent via A2A...")
            task_request = A2ARequest(
                method="tasks/execute",
                params={
                    "task_id": "0",
                    "instruction": "List all high-priority tickets",
                    "tools": [
                        {"name": "list_tickets", "description": "List all tickets"}
                    ],
                },
                id="task_1",
            )
            task_response = await client.post(
                "http://localhost:8001/a2a/execute_task",
                json=task_request.model_dump(),
            )
            print(f"   Status: {task_response.status_code}")
            print(f"   Response: {json.dumps(task_response.json(), indent=2)}")
            
            # Test 6: Orchestrate via green agent
            print("\n7. Orchestrating task through green agent...")
            orchestrate_request = {
                "jsonrpc": "2.0",
                "method": "tasks/execute",
                "params": {
                    "assessment_id": assessment_id,
                    "task_id": "0",
                    "instruction": "List all high-priority tickets",
                    "tools": [
                        {"name": "list_tickets", "description": "List all tickets"}
                    ],
                },
                "id": "orchestrate_1",
            }
            orch_response = await client.post(
                "http://localhost:8000/a2a/execute_task",
                json=orchestrate_request,
            )
            print(f"   Status: {orch_response.status_code}")
            orch_data = orch_response.json()
            print(f"   Response: {json.dumps(orch_data, indent=2)}")
            
            # Test 7: Get result
            print(f"\n8. Retrieving assessment result {assessment_id}...")
            result_response = await client.get(
                f"http://localhost:8000/a2a/result/{assessment_id}"
            )
            print(f"   Status: {result_response.status_code}")
            print(f"   Response: {json.dumps(result_response.json(), indent=2)}")
            
            print("\n" + "=" * 70)
            print("✓ All tests completed successfully!")
            print("=" * 70)
            
    finally:
        print("\nCleaning up...")
        white_agent_proc.terminate()
        white_agent_proc.wait(timeout=5)


if __name__ == "__main__":
    asyncio.run(test_a2a_integration())
