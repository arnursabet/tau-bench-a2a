.PHONY: setup run demo test clean a2a-test mock-agent

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install -q -r requirements.txt || pip install -q litellm openai anthropic google-generativeai tenacity termcolor numpy fastapi uvicorn httpx pydantic

run:
	. venv/bin/activate && uvicorn service.green_agent.main:app --reload

demo:
	. venv/bin/activate && python3 scripts/demo.py

test:
	. venv/bin/activate && python3 -m pytest tests/ -v

clean:
	rm -rf venv data logs __pycache__ .pytest_cache

cli-pm:
	. venv/bin/activate && python3 run.py --agent-strategy tool-calling --env pm --model gpt-4-mini --model-provider openai --num-trials 1 --user-model gpt-4-mini --user-model-provider openai --max-concurrency 1

# A2A Protocol Integration Tests

mock-agent:
	. venv/bin/activate && python3 -m uvicorn service.mock_white_agent:app --host 127.0.0.1 --port 8001

a2a-test:
	. venv/bin/activate && python3 scripts/test_a2a_integration.py
