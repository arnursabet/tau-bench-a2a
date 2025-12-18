# τ-Bench Project Management (PM) Domain

This extension adds a **project management domain** to τ-Bench, enabling evaluation of agents on realistic ticket-management tasks.

## Quick Start

```bash
python3 -m venv venv && source venv/bin/activate && pip install -e .
cp env.example .env  # Add your OPENAI_API_KEY to .env
./venv/bin/python run.py --env pm --model gpt-4o-mini --model-provider openai --user-model gpt-4o-mini --user-model-provider openai --num-trials 3
```

---

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

## Quick Start

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Set up environment variables
cp env.example .env
```

### Configure OpenAI API Key

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
LLM_MODEL=gpt-4o-mini
USE_MOCK_WHITE_AGENT=false
```

You can obtain an API key from [OpenAI Platform](https://platform.openai.com/api-keys).

### Run Evaluation

```bash
# Run white agent (GPT-4o-mini) on PM domain tasks
./venv/bin/python run.py \
  --agent-strategy tool-calling \
  --env pm \
  --model gpt-4o-mini \
  --model-provider openai \
  --user-model gpt-4o-mini \
  --user-model-provider openai \
  --num-trials 3
```

---

## Green Agent (Evaluator)

The Green Agent is the evaluation service that tests White Agents on project management tasks. It implements the A2A (Agent-to-Agent) protocol for AgentBeats compatibility.

### What the Green Agent Does

1. Sets up the PM domain environment with users, projects, and tickets
2. Sends task instructions and available tools to White Agents
3. Receives tool calls from White Agents and executes them against the environment
4. Evaluates responses by comparing final state against ground truth
5. Computes metrics (pass^1, pass^k, reward)

### Running the Green Agent Service

```bash
# Start the Green Agent FastAPI service
uvicorn service.green_agent.main:app --host 0.0.0.0 --port 8000 --reload
```

### Green Agent Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/a2a/agent-card` | GET | A2A agent capabilities descriptor |
| `/.well-known/agent-card.json` | GET | Agent card discovery endpoint |
| `/a2a/register_agent` | POST | Register a White Agent for assessment |
| `/a2a/execute_task` | POST | Execute a task and evaluate response |
| `/a2a/result/{assessment_id}` | GET | Fetch assessment results |
| `/a2a/reset` | POST | Reset environment state |

### Testing Green Agent Evaluation

```bash
# Run A2A integration test (tests full green-white agent flow)
python scripts/test_a2a_integration.py

# Run simple green agent test
python test_simple.py
```

---

## White Agent (Agent Being Evaluated)

The White Agent is the AI agent being tested. It receives task instructions and must execute the correct sequence of tool calls to complete project management workflows.

### Running White Agents via CLI

The simplest way to run a White Agent is through the CLI, which handles the full evaluation loop:

```bash
# Run GPT-4o-mini as White Agent (recommended for testing)
./venv/bin/python run.py \
  --agent-strategy tool-calling \
  --env pm \
  --model gpt-4o-mini \
  --model-provider openai \
  --user-model gpt-4o-mini \
  --user-model-provider openai \
  --num-trials 3

# Run GPT-4o as White Agent (better performance, higher cost)
./venv/bin/python run.py \
  --agent-strategy tool-calling \
  --env pm \
  --model gpt-4o \
  --model-provider openai \
  --user-model gpt-4o \
  --user-model-provider openai \
  --num-trials 3

# Run on specific tasks only
./venv/bin/python run.py \
  --env pm \
  --model gpt-4o-mini \
  --model-provider openai \
  --task-ids 0 2 3 \
  --num-trials 1
```

### Running White Agent as A2A Service

For A2A protocol integration, run the White Agent as a separate service:

```bash
# Start White Agent service on port 8001
uvicorn service.white_agent.main:app --host 0.0.0.0 --port 8001 --reload

# Or use the mock White Agent for testing (no LLM required)
uvicorn service.mock_white_agent:app --host 0.0.0.0 --port 8001
```

### White Agent Strategies

| Strategy | Description | Command Flag |
|----------|-------------|--------------|
| `tool-calling` | Native LLM function calling (default) | `--agent-strategy tool-calling` |
| `react` | ReAct reasoning + acting | `--agent-strategy react` |
| `act` | Act-only (no explicit reasoning) | `--agent-strategy act` |

---

## Reproducing Benchmark Results

### Reproduce PM Domain Results

To reproduce our evaluation results (GPT-4o-mini, pass^1 = 40%):

```bash
# Exact reproduction command
./venv/bin/python run.py \
  --agent-strategy tool-calling \
  --env pm \
  --model gpt-4o-mini \
  --model-provider openai \
  --user-model gpt-4o-mini \
  --user-model-provider openai \
  --num-trials 3 \
  --seed 10

# Results will be saved to results/ directory
```

Expected output:
```
Running tasks 0 to 5
Task 0: FAIL (0% pass rate)
Task 1: FAIL (0% pass rate)
Task 2: PASS (100% pass rate)
Task 3: PASS (100% pass rate)
Task 4: FAIL (0% pass rate)

Average reward: 0.4
Pass^1: 0.4
Pass^2: 0.4
Pass^3: 0.4
```

### Reproduce Original t-Bench Results (Retail/Airline)

This implementation is based on the original t-Bench benchmark. To run evaluations on the original domains:

```bash
# Run on retail domain
./venv/bin/python run.py \
  --env retail \
  --model gpt-4o \
  --model-provider openai \
  --user-model gpt-4o \
  --user-model-provider openai \
  --num-trials 1

# Run on airline domain
./venv/bin/python run.py \
  --env airline \
  --model gpt-4o \
  --model-provider openai \
  --user-model gpt-4o \
  --user-model-provider openai \
  --num-trials 1
```

Reference results from original t-Bench paper:
- GPT-4o on retail: ~61% pass^1
- GPT-4o on airline: ~35% pass^1

---

## Programmatic Usage

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

---

## AgentBeats Deployment

This Green Agent is designed to run on the AgentBeats platform.

### Procfile Configuration

```
web: agentbeats run_ctrl
```

### Agent Card Location

The agent card is served at `/.well-known/agent-card.json` for A2A discovery.

## Metrics

The evaluation framework tracks:

- **pass^1**: Fraction of tasks completed successfully in one trial
- **pass^k**: Probability of completing all k trials successfully (measures consistency/reliability)
- **Per-task metrics**: Task-level pass rates and pass^k breakdown
- **Episode logs**: Action sequences, errors, and policy violations

## Demo & Testing

### Run Demo (Mock White Agent)

The demo script uses a mock white agent simulator (no LLM API calls required):

```bash
make demo
# or
python3 scripts/demo.py
```

Generates `demo_results.json` with sample assessment results using simulated responses.

### Run Real Evaluations

For actual LLM-based evaluation (requires OpenAI API key in `.env`):

```bash
# Run GPT-4o-mini on all PM tasks
./venv/bin/python run.py \
  --agent-strategy tool-calling \
  --env pm \
  --model gpt-4o-mini \
  --model-provider openai \
  --user-model gpt-4o-mini \
  --user-model-provider openai \
  --num-trials 3

# Results saved to results/ directory
```

### Expected Output (Real Evaluation)

```
Running tasks 0 to 5
Task 0: FAIL (0% pass rate)
Task 1: FAIL (0% pass rate)
Task 2: PASS (100% pass rate)
Task 3: PASS (100% pass rate)
Task 4: FAIL (0% pass rate)

Average reward: 0.4
Pass^1: 0.4
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
├── README.md                 # This file
├── setup.py                  # Package installation
├── run.py                    # CLI entry point for evaluations
├── env.example               # Environment variable template
├── Makefile                  # Build and run targets
├── Procfile                  # AgentBeats deployment config
│
├── tau_bench/
│   ├── envs/
│   │   ├── base.py           # Base environment class
│   │   ├── pm/               # Project Management domain
│   │   │   ├── env.py        # PM environment implementation
│   │   │   ├── data/
│   │   │   │   ├── users.json
│   │   │   │   ├── projects.json
│   │   │   │   └── tickets.json
│   │   │   ├── tools/        # 9 tool implementations
│   │   │   ├── wiki.md       # Policy documentation
│   │   │   ├── rules.py      # Rule definitions
│   │   │   └── tasks_test.py # 5 test tasks
│   │   ├── retail/           # Original retail domain
│   │   └── airline/          # Original airline domain
│   │
│   ├── agents/               # Agent implementations
│   │   ├── tool_calling_agent.py
│   │   ├── chat_react_agent.py
│   │   └── base.py
│   │
│   └── model_utils/          # LLM API utilities
│
├── service/
│   ├── green_agent/          # Evaluator service (A2A)
│   │   ├── main.py           # FastAPI application
│   │   ├── runner.py         # Assessment runner
│   │   ├── schemas.py        # Pydantic models
│   │   ├── a2a_schemas.py    # A2A protocol schemas
│   │   └── config.py         # Configuration
│   │
│   └── white_agent/          # White agent service (A2A)
│       ├── main.py           # FastAPI application
│       └── llm_agent.py      # LLM-based agent
│
└── scripts/
    ├── demo.py               # Demo assessment script
    └── test_a2a_integration.py  # A2A integration tests
```

## References

- τ-Bench paper: https://arxiv.org/abs/2406.12045
- τ-Bench repo: https://github.com/sierra-research/tau-bench
