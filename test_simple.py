"""Simple Python test to verify green agent works."""
import requests
import json

base_url = "http://127.0.0.1:8000"

print("=== Simple Green Agent Test ===\n")

# 1. Register white agent
print("1. Registering white agent...")
register_response = requests.post(
    f"{base_url}/a2a/register_agent",
    json={"agent_url": "http://localhost:8001", "agent_card": None}
)
assessment_id = register_response.json()["assessment_id"]
print(f"   ✓ Registered: {assessment_id}\n")

# 2. Execute task
print("2. Executing task...")
task_response = requests.post(
    f"{base_url}/a2a/execute_task",
    json={
        "jsonrpc": "2.0",
        "method": "tasks/execute",
        "params": {
            "assessment_id": assessment_id,
            "task_id": "0",
            "instruction": "List all tickets",
            "tools": []
        },
        "id": "test_1"
    }
)

print(f"   Status Code: {task_response.status_code}\n")

# 3. Display result
result = task_response.json()
print("3. Result:")
print(json.dumps(result, indent=2))

# 4. Check for errors
if "error" in result:
    print("\n❌ ERROR:", result["error"])
elif "result" in result:
    print("\n✅ SUCCESS!")
    if "evaluation" in result["result"]:
        eval_data = result["result"]["evaluation"]
        print(f"   Reward: {eval_data.get('reward', 'N/A')}")
        print(f"   Status: {eval_data.get('status', 'N/A')}")
else:
    print("\n⚠️  Unexpected response format")

