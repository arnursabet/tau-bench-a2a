
import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


# Valid status transitions
ALLOWED_TRANSITIONS = {
    "todo": ["in_progress"],
    "in_progress": ["in_review", "todo"],
    "in_review": ["done", "in_progress"],
    "done": [],
}


class UpdateStatus(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], ticket_id: str, new_status: str) -> str:
        """Update the status of a ticket. Must follow allowed transitions."""
        tickets = data["tickets"]
        if ticket_id not in tickets:
            return "Error: ticket not found"
        
        ticket = tickets[ticket_id]
        current_status = ticket["status"]
        
        if new_status not in ALLOWED_TRANSITIONS.get(current_status, []):
            return f"Error: cannot transition from {current_status} to {new_status}"
        
        ticket["status"] = new_status
        ticket["history"].append({
            "action": "status_updated",
            "from": current_status,
            "to": new_status,
            "timestamp": "2024-10-20T00:00:00",
        })
        return json.dumps(ticket)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_status",
                "description": "Update the status of a ticket. Follow these transitions: todo→in_progress, in_progress→in_review or todo, in_review→done or in_progress.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {
                            "type": "string",
                            "description": "The ticket ID.",
                        },
                        "new_status": {
                            "type": "string",
                            "description": "The new status (todo, in_progress, in_review, done).",
                        },
                    },
                    "required": ["ticket_id", "new_status"],
                },
            },
        }
