

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class UpdatePriority(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], ticket_id: str, priority: str) -> str:
        """Update the priority of a ticket."""
        if priority not in ["low", "medium", "high"]:
            return "Error: priority must be low, medium, or high"
        
        tickets = data["tickets"]
        if ticket_id not in tickets:
            return "Error: ticket not found"
        
        ticket = tickets[ticket_id]
        old_priority = ticket["priority"]
        ticket["priority"] = priority
        ticket["history"].append({
            "action": "priority_updated",
            "from": old_priority,
            "to": priority,
            "timestamp": "2024-10-20T00:00:00",
        })
        return json.dumps(ticket)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_priority",
                "description": "Update the priority of a ticket.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The ticket ID.",
                        },
                        "priority": {
                            "type": "string",
                            "description": "The new priority (low, medium, high).",
                        },
                    },
                    "required": ["ticket_id", "priority"],
                },
            },
        }
