# τ-Bench Project Management (PM) Domain

This extension adds a **project management domain** to τ-Bench, enabling evaluation of agents on realistic ticket-management tasks.

## Overview

The PM domain evaluates agents on their ability to:
- Authenticate users and operate within project scope
- Create, update, and manage tickets (tasks)
- Assign tickets to team members
- Enforce policy constraints (status transitions, membership checks, confirmation rules)
- Handle multi-step workflows consistently

## Domain Components

### Data Model

**Users** (`data/users.json`):
- 5 sample users with IDs, names, and emails
- Used for authentication and project membership

**Projects** (`data/projects.json`):
- 3 projects: Web App, Mobile, Backend
- Each project has a defined member list

**Tickets** (`data/tickets.json`):
- Initial set of 5 tickets across projects
- Fields: id, project_id, title, description, status, priority, assignee, comments, history

### Tools (APIs)

Located in `tau_bench/envs/pm/tools/`:

| Tool | Purpose |
|------|---------|
| `list_tickets` | Query tickets in a project with optional status filter |
| `create_ticket` | Create a new ticket with title, description, priority |
| `update_status` | Change ticket status following allowed transitions |
| `assign_user` | Assign ticket to a project member |
| `update_priority` | Change ticket priority (low/medium/high) |
| `add_comment` | Add a comment to a ticket |
| `get_user_details` | Retrieve user information |
| `transfer_to_human_agents` | Terminate conversation (for out-of-scope requests) |
| `think` | Internal reasoning (non-state-changing) |

### Policy

Defined in `tau_bench/envs/pm/wiki.md` and `tau_bench/envs/pm/rules.py`:

- **Authentication**: User must be identified at the beginning
- **Single Project Scope**: Agent works on one project per conversation
- **Status Transitions**: `todo → in_progress → in_review → done` (with backtracking allowed)
- **Membership Constraint**: Only project members can be assigned tickets
- **Confirmation**: Agent must ask for explicit confirmation before state-changing operations
- **One Call per Turn**: Either a tool call OR user response, never both

### Tasks

5 test tasks in `tau_bench/envs/pm/tasks_test.py` covering:
1. Assigning high-priority tickets and moving to in_progress
2. Creating multiple new tickets with different priorities
3. Moving a ticket through status workflow
4. Assigning and changing priority
5. Adding comments and completing a ticket

## Integration with τ-Bench

### Using the CLI

```bash
# Load the PM domain
python run.py \
  --agent-strategy tool-calling \
  --env pm \
  --model gpt-4-mini \
  --model-provider openai \
  --num-trials 3 \
  --user-model gpt-4-mini \
  --user-model-provider openai
```

### Programmatic Usage

```python
from tau_bench.envs import get_env

env = get_env(
    env_name="pm",
    user_strategy="llm",  # or "human" for interactive testing
    user_model="gpt-4o",
    task_split="test",
)

# Access domain components
print(f"Tasks: {len(env.tasks)}")
print(f"Tools: {len(env.tools_info)}")
print(f"Wiki: {len(env.wiki)}")
```

## FastAPI Green Agent Service

A FastAPI service exposes the PM domain for evaluation:

### Installation

```bash
pip install fastapi uvicorn
```

### Running the Service

```bash
make run
# or
uvicorn service.green_agent.main:app --reload
```

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/agent-card` | GET | Agent capabilities descriptor |
| `/reset` | POST | Reset domain state |
| `/assess` | POST | Run assessment on tasks |
| `/logs/{run_id}` | GET | Fetch run logs and episodes |

### Example: Running an Assessment

```bash
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{
    "trials": 3,
    "agent_strategy": "tool-calling",
    "task_ids": [0, 1, 2]
  }'
```

Response:
```json
{
  "run_id": "762ecd18-b2b6-497f-9129-3e4ff8b71aed",
  "pass_1": 0.4,
  "pass_k": {"1": 0.4, "2": 0.2, "3": 0.0},
  "per_task": [
    {
      "task_id": 0,
      "pass_1": 0.333,
      "pass_k": {"1": 0.333, "2": 0.0, "3": 0.0},
      "num_trials": 3
    },
    ...
  ]
}
```

## Metrics

The evaluation framework tracks:

- **pass^1**: Fraction of tasks completed successfully in one trial
- **pass^k**: Probability of completing all k trials successfully (measures consistency/reliability)
- **Per-task metrics**: Task-level pass rates and pass^k breakdown
- **Episode logs**: Action sequences, errors, and policy violations

## Demo & Testing

### Run Demo

```bash
make demo
# or
python3 scripts/demo.py
```

Generates `demo_results.json` with sample assessment results.

### Expected Output

```
============================================================
τ-Bench PM Domain Demo
============================================================

Running Assessment 1: Basic eval (1 trial)
------------------------------------------------------------
Run ID: ...
Pass^1: 40.00%
Pass^k: {1: 0.4}

Running Assessment 2: Multi-trial eval (3 trials)
------------------------------------------------------------
...
```

## Design Rationale

### Simplicity & DRY

- Reuses τ-Bench's core evaluation harness (environment, agent framework, metrics)
- Tools follow τ-Bench patterns (Tool base class, get_info descriptors, invoke methods)
- No SQL; state is pure JSON for tractability

### Policy Enforcement

- Status transitions hard-coded in `UpdateStatus` tool
- Membership checks in `AssignUser` tool
- Policy text echoed in system prompt for LLM agents

### Ground Truth Validation

- Tasks include deterministic action sequences
- Final state compared via JSON hash (like retail/airline domains)
- Output verification for user-facing information (comments, confirmations)

## Future Improvements

1. **Real Agent Integration**: Replace mock rewards with actual agent/LLM invocation
2. **More Tasks**: Expand test/dev/train splits with complex scenarios
3. **Advanced Policies**: Dynamic rules, multi-project workflows, role-based access
4. **Metrics Extensions**: Cost tracking, latency, error categories
5. **Baseline Agents**: Implement rule-based and few-shot baselines

## File Structure

```
tau_bench/
├── envs/
│   ├── pm/
│   │   ├── __init__.py
│   │   ├── env.py           # MockPMDomainEnv
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── users.json
│   │   │   ├── projects.json
│   │   │   └── tickets.json
│   │   ├── tools/           # Tool implementations
│   │   ├── wiki.md          # Policy documentation
│   │   ├── wiki.py          # Wiki loader
│   │   ├── rules.py         # Rule list
│   │   └── tasks_test.py    # Test tasks
│
service/
├── green_agent/
│   ├── main.py              # FastAPI app
│   ├── schemas.py           # Pydantic models
│   ├── runner.py            # Assessment runner
│   ├── storage.py           # SQLite storage
│   └── config.py            # Configuration
│
scripts/
├── demo.py                  # Demo assessment script
└── Makefile                 # Build/run targets
```

## References

- τ-Bench paper: https://arxiv.org/abs/2406.12045
- τ-Bench repo: https://github.com/sierra-research/tau-bench
