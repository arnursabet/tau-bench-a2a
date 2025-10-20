
import json
from typing import Any, Dict
from tau_bench.envs.tool import Tool


class Think(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], thought: str) -> str:
        """Add an internal thought/reasoning note (does not affect state)."""
        return json.dumps({"thought": thought})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "think",
                "description": "Think through a problem or reasoning step. This does not affect the state and is only for your internal use.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "thought": {
                            "type": "string",
                            "description": "Your thought process or reasoning.",
                        },
                    },
                    "required": ["thought"],
                },
            },
        }
