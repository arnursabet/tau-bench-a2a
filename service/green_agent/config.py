
import os
from pathlib import Path

# Service configuration
SERVICE_NAME = "τ-Bench PM Green Agent"
SERVICE_VERSION = "0.1.0"
DOMAIN = "pm"

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "data" / "green_agent.db"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
os.makedirs(DB_PATH.parent, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Metrics tracked
METRICS = [
    "pass_1",
    "pass_k",
    "avg_reward",
    "task_success_rate",
]
