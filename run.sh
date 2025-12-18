set -e

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python -m uvicorn service.green_agent.main:app --host ${HOST:-0.0.0.0} --port ${AGENT_PORT:-8000}
