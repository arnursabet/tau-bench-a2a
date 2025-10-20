

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class GetUserDetails(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], user_id: str) -> str:
        """Get details about a user."""
        users = data["users"]
        if user_id not in users:
            return "Error: user not found"
        return json.dumps(users[user_id])

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_user_details",
                "description": "Get the details of a user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user ID, such as 'alice_smith_1001'.",
                        },
                    },
                    "required": ["user_id"],
                },
            },
        }
