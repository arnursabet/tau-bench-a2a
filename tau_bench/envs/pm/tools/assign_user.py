

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AssignUser(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], ticket_id: str, user_id: str) -> str:
        """Assign a ticket to a user. User must be a project member."""
        tickets = data["tickets"]
        if ticket_id not in tickets:
            return "Error: ticket not found"
        
        users = data["users"]
        if user_id not in users:
            return "Error: user not found"
        
        ticket = tickets[ticket_id]
        projects = data["projects"]
        project = projects[ticket["project_id"]]
        
        if user_id not in project["members"]:
            return f"Error: user {user_id} is not a member of project {ticket['project_id']}"
        
        ticket["assignee"] = user_id
        ticket["history"].append({
            "action": "assigned",
            "user": user_id,
            "timestamp": "2024-10-20T00:00:00",
        })
        return json.dumps(ticket)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "assign_user",
                "description": "Assign a ticket to a project member.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The ticket ID.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "The user ID. Must be a project member.",
                        },
                    },
                    "required": ["ticket_id", "user_id"],
                },
            },
        }
