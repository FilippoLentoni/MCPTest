## Context

The `weather-tool` Lambda is already deployed and invokable via `boto3`. The MCP gateway path works for interactive Claude Code sessions but adds latency and auth complexity for scripted/batch use. The CLI-Anything project proves that a Click CLI with `--json` output and `SKILL.md` is the right agent-native pattern. This CLI wraps the Lambda invocation directly.

## Goals / Non-Goals

**Goals:**
- `weather-cli get --city <city>` invokes `weather-tool` Lambda via `boto3` and prints the result
- `--json` flag emits a JSON object (success or error) suitable for shell piping and agent parsing
- `pip install -e src/weather_tool_cli` puts `weather-cli` on `PATH`
- `SKILL.md` at repo root documents the CLI for agent discovery

**Non-Goals:**
- No new AWS infrastructure (Lambda, gateway, CDK — all unchanged)
- No streaming or async invocation (Lambda is synchronous, payload < 6 MB)
- No configuration file or `.env` management — credentials come from the standard AWS credential chain
- No support for invoking other Lambdas — this is a single-purpose tool

## Decisions

### D1 — Click over argparse

Click produces `--help` output that reads naturally as a SKILL.md description and handles `--json` as a boolean flag cleanly. argparse would require more boilerplate for the same result.

### D2 — Direct `boto3` invocation, not `aws lambda invoke` subprocess

`boto3` gives structured error objects (no shell parsing), respects the full credential chain (env vars, profiles, instance roles), and avoids a subprocess layer that could mask errors or complicate testing.

### D3 — `src/weather_tool_cli/` layout, separate from `src/weather_tool/`

The CLI is a client — it calls the deployed Lambda over the network. It has no business logic in common with the handler. Keeping it in its own package prevents accidental coupling and lets it be installed independently.

### D4 — Error output also as JSON when `--json` is set

Agents that parse `--json` output must handle errors without switching parsers. The error response is `{"error": "<message>", "exit_code": 1}` — same structure, non-zero exit so shell `&&` chains break correctly.

## Risks / Trade-offs

- **[Risk] AWS credentials not configured** → `boto3` raises `NoCredentialsError`; caught and emitted as `{"error": "AWS credentials not found..."}` with exit 1.
- **[Risk] Lambda cold start adds latency** → Acceptable; the Lambda is already warm during active dev sessions. No mitigation needed.
- **[Risk] Lambda ARN hardcoded vs. configurable** → Hardcoded to `weather-tool` function name in `us-east-1` for now. A future change can add `--region` / `--function` flags if needed.
