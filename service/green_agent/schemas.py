
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class AssessmentRequest(BaseModel):
    """Request body for /assess endpoint."""
    trials: int = 1
    task_ids: Optional[List[int]] = None
    agent_strategy: str = "tool-calling"


class MetricsResult(BaseModel):
    """Metrics for a single task."""
    task_id: int
    pass_1: float
    pass_k: Dict[int, float]
    num_trials: int


class AssessmentResponse(BaseModel):
    """Response from /assess endpoint."""
    run_id: str
    pass_1: float
    pass_k: Dict[int, float]
    per_task: List[MetricsResult]


class AgentCard(BaseModel):
    """Agent capabilities descriptor."""
    name: str
    domain: str
    version: str
    metrics: List[str]
