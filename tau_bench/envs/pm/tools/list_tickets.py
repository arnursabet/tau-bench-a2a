
import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class ListTickets(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], project_id: str, status: str = None) -> str:
        """List tickets in a project, optionally filtered by status."""
        tickets = data["tickets"]
        result = []
        for ticket_id, ticket in tickets.items():
            if ticket["project_id"] == project_id:
                if status is None or ticket["status"] == status:
                    result.append({
                        "id": ticket["id"],
                        "title": ticket["title"],
                        "status": ticket["status"],
                        "priority": ticket["priority"],
                        "assignee": ticket["assignee"],
                    })
        return json.dumps(result)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "list_tickets",
                "description": "List all tickets in a project, optionally filtered by status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The project ID, e.g., 'proj_web_app_2024'.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional status filter (todo, in_progress, in_review, done).",
                        },
                    },
                    "required": ["project_id"],
                },
            },
        }
