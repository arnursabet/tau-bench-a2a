# Project Implementation Notes

This document provides additional implementation details for the tau-Bench PM Domain white agent project.

## Development Setup

### Running Tests

```bash
# Unit tests for LLM functionality
python test_llm_direct.py

# Integration tests (green-white agent interaction)
python test_integration.py

# Full end-to-end with real LLM
python test_with_real_llm.py
```

### Debug Commands

```bash
# Check agent health
curl http://localhost:8000/health
curl http://localhost:8002/health

# Check agent cards
curl http://localhost:8000/.well-known/agent-card.json
curl http://localhost:8002/.well-known/agent-card.json
```

## Execution Modes

| Mode | Description | Configuration |
|------|-------------|---------------|
| Real | Uses LLM white agent | `USE_MOCK_WHITE_AGENT=false` (default) |
| Mock | Uses simulated responses | `USE_MOCK_WHITE_AGENT=true` |

## Troubleshooting

### API Key Issues
- Verify `.env` file exists with `OPENAI_API_KEY=your-key`
- Run `python test_llm_direct.py` to verify API access

### Port Conflicts
- Green agent uses port 8000
- White agent uses port 8002
- Check for conflicts: `lsof -i :8000` and `lsof -i :8002`

### Agent Communication Failures
- Verify both agents are running before testing
- Check `launcher.py` output for connection errors

## Additional Resources

- Main documentation: [README.md](README.md)
- Original tau-Bench: [TAU-BENCH-README.md](TAU-BENCH-README.md)
- PM Domain policy: [tau_bench/envs/pm/wiki.md](tau_bench/envs/pm/wiki.md)
