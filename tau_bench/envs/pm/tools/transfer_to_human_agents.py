
import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class TransferToHumanAgents(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], summary: str) -> str:
        """Transfer the conversation to a human agent."""
        return json.dumps({"status": "transferred", "summary": summary})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "transfer_to_human_agents",
                "description": "Transfer the conversation to a human agent when the task cannot be handled.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "A summary of the issue to pass to the human agent.",
                        },
                    },
                    "required": ["summary"],
                },
            },
        }
