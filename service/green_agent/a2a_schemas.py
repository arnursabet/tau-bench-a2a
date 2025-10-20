
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union


# A2A Message Wrapper (JSON-RPC 2.0)
class A2ARequest(BaseModel):
    """A2A Protocol request using JSON-RPC 2.0 format."""
    jsonrpc: str = "2.0"
    method: str  # e.g., "tasks/execute", "agent/reset"
    params: Dict[str, Any]
    id: Union[str, int]


class A2AResponse(BaseModel):
    """A2A Protocol response using JSON-RPC 2.0 format."""
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Union[str, int]


# Agent Card (A2A Format)
class AgentCapabilities(BaseModel):
    """Describes what an agent can do."""
    domains: List[str]
    metrics: List[str]
    max_agents: Optional[int] = None
    max_trials: Optional[int] = None
    max_concurrent_tasks: int = 1


class AgentEndpoints(BaseModel):
    """API endpoints exposed by the agent."""
    agent_card: str
    reset: Optional[str] = None
    execute_task: str
    get_result: Optional[str] = None
    register_agent: Optional[str] = None


class AgentCard(BaseModel):
    """A2A Agent Card - Self-description of agent capabilities."""
    name: str
    description: str
    version: str
    protocol: str = "a2a"
    capabilities: AgentCapabilities
    endpoints: AgentEndpoints
    authentication: Optional[str] = None


# Task Execution (A2A Format)
class TaskInput(BaseModel):
    """Input for task execution."""
    task_id: str
    instruction: str
    tools: List[Dict[str, Any]]  # Tool schemas
    environment_state: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


class TaskOutput(BaseModel):
    """Output from task execution."""
    task_id: str
    status: str  # "success", "failure", "error"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float


# Assessment Request & Result
class AssessmentRequest(BaseModel):
    """Request to run an assessment."""
    agent_urls: List[str]  # URLs of white agents to evaluate
    num_trials: int = 1
    task_ids: Optional[List[int]] = None
    agent_strategy: str = "tool-calling"


class TaskMetrics(BaseModel):
    """Metrics for a single task."""
    task_id: int
    pass_1: float
    pass_k: Dict[int, float]
    num_trials: int
    policy_violations: int = 0


class AssessmentResult(BaseModel):
    """Result of an assessment."""
    assessment_id: str
    pass_1: float
    pass_k: Dict[int, float]
    per_task: List[TaskMetrics]
    agent_urls: List[str]
    timestamp: str
    status: str = "completed"


# Agent Registration
class AgentRegistration(BaseModel):
    """White agent registration."""
    agent_url: str
    agent_card: Optional[AgentCard] = None
    submission_time: Optional[str] = None


class RegistrationResponse(BaseModel):
    """Response to registration."""
    status: str  # "accepted", "rejected"
    assessment_id: str
    message: Optional[str] = None
