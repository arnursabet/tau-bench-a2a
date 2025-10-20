import json
import os
from typing import Any, Dict


def load_data() -> Dict[str, Any]:
    """Load PM domain data from JSON files."""
    data_dir = os.path.dirname(__file__)
    users = json.load(open(os.path.join(data_dir, "users.json")))
    projects = json.load(open(os.path.join(data_dir, "projects.json")))
    tickets = json.load(open(os.path.join(data_dir, "tickets.json")))
    return {
        "users": users,
        "projects": projects,
        "tickets": tickets,
    }
