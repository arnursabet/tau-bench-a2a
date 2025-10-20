

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class AddComment(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], ticket_id: str, comment: str) -> str:
        """Add a comment to a ticket."""
        tickets = data["tickets"]
        if ticket_id not in tickets:
            return "Error: ticket not found"
        
        ticket = tickets[ticket_id]
        ticket["comments"].append({
            "text": comment,
            "timestamp": "2024-10-20T00:00:00",
        })
        return json.dumps(ticket)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_comment",
                "description": "Add a comment to a ticket.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The ticket ID.",
                        },
                        "comment": {
                            "type": "string",
                            "description": "The comment text.",
                        },
                    },
                    "required": ["ticket_id", "comment"],
                },
            },
        }
