## Why

The MCP gateway works for interactive Claude Code sessions, but a coding agent also needs to invoke the `weather-tool` Lambda directly from the shell — for scripting, testing, and batch workflows where spinning up an MCP session is unnecessary overhead. A lightweight CLI following the CLI-Anything pattern (Click + `--json` + `SKILL.md`) gives agents a discoverable, scriptable interface that calls the Lambda via `boto3` with no gateway in the path.

## What Changes

- New Python CLI package at `src/weather_tool_cli/` — Click-based, installable via `pip install -e .`
- `weather get --city <city>` subcommand invokes the Lambda directly via `boto3.lambda_.invoke`
- `--json` flag returns machine-readable output (structured JSON or error object)
- `SKILL.md` at repo root describing the CLI for agent discovery
- `src/weather_tool_cli/setup.py` so the CLI lands on `PATH` as `weather-cli`

## Capabilities

### New Capabilities

- `weather-tool-cli`: Agent-native CLI for invoking the `weather-tool` Lambda directly, with structured JSON output and shell-scriptable interface

### Modified Capabilities

_(none — gateway, Lambda, and MCP registration are unchanged)_

## Impact

- New source tree: `src/weather_tool_cli/` (does not affect existing `src/weather_tool/`)
- New dev dependency: `click` (already available in the venv; no CDK changes)
- `SKILL.md` added at repo root for agent discovery
- AWS credentials with `lambda:InvokeFunction` on `weather-tool` required at runtime (already present in the `columbia` profile)
