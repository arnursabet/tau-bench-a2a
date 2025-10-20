

import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class CreateTicket(Tool):
    @staticmethod
    def invoke(
        data: Dict[str, Any],
        project_id: str,
        title: str,
        description: str,
        priority: str = "medium",
    ) -> str:
        """Create a new ticket in a project."""
        projects = data["projects"]
        if project_id not in projects:
            return "Error: project not found"
        
        tickets = data["tickets"]
        ticket_id = f"tick_{len(tickets) + 100}"
        new_ticket = {
            "id": ticket_id,
            "project_id": project_id,
            "title": title,
            "description": description,
            "status": "todo",
            "priority": priority,
            "assignee": None,
            "comments": [],
            "history": [],
        }
        tickets[ticket_id] = new_ticket
        return json.dumps(new_ticket)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_ticket",
                "description": "Create a new ticket in a project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The project ID.",
                        },
                        "title": {
                            "type": "string",
                            "description": "The ticket title.",
                        },
                        "description": {
                            "type": "string",
                            "description": "The ticket description.",
                        },
                        "priority": {
                            "type": "string",
                            "description": "Priority level: low, medium, or high.",
                        },
                    },
                    "required": ["project_id", "title", "description"],
                },
            },
        }
