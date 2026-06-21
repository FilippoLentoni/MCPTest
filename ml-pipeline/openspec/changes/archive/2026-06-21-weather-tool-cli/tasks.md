## 1. Package Structure

- [x] 1.1 Create `src/weather_tool_cli/` directory with `__init__.py`
- [x] 1.2 Create `src/weather_tool_cli/cli.py` — Click app with `get` subcommand and `--json` flag
- [x] 1.3 Create `src/weather_tool_cli/setup.py` with `weather-cli` entry point

## 2. CLI Implementation

- [x] 2.1 Implement `get_weather` function in `cli.py` — calls `boto3.client('lambda').invoke` with `FunctionName='weather-tool'` and `Payload={"city": city}`
- [x] 2.2 Handle success: parse Lambda response payload, print result (human or JSON)
- [x] 2.3 Handle errors: Lambda errors, `NoCredentialsError`, missing city — emit `{"error": "..."}` with exit 1 when `--json`

## 3. Install and Smoke Test

- [x] 3.1 Run `pip install -e src/weather_tool_cli` in the project venv
- [x] 3.2 Run `weather-cli --help` and confirm command is on PATH
- [x] 3.3 Run `weather-cli get --city Tokyo` — confirm structured weather output
- [x] 3.4 Run `weather-cli get --city Tokyo --json` — confirm valid JSON with all required keys

## 4. SKILL.md

- [x] 4.1 Create `SKILL.md` at repo root describing `weather-cli` commands, flags, JSON output schema, and install instructions
