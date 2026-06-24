# weather-cli

Agent-native CLI for invoking the `weather-tool` Lambda directly via `boto3`. No MCP gateway required.

## Install

```bash
pip install -e src/weather_tool_cli
```

Requires Python 3.10+ and AWS credentials with `lambda:InvokeFunction` on the `weather-tool` function in `us-east-1`.

## Commands

### `weather-cli get --city <city>`

Invoke the `weather-tool` Lambda and return current weather for the given city.

**Options:**

| Flag | Description |
|------|-------------|
| `--city TEXT` | City name, e.g. `Tokyo` or `New York` *(required)* |
| `--profile TEXT` | AWS profile name (overrides `AWS_PROFILE` env var) |
| `--json` | Emit machine-readable JSON instead of human-readable text |
| `--help` | Show help and exit |

**Human output (default):**

```
City:        Tokyo
Condition:   Clear
Temperature: 23°C / 73°F
Humidity:    78%
Wind:        59 kph
```

**JSON output (`--json` flag):**

```json
{
  "city": "Tokyo",
  "temperature_c": 23,
  "temperature_f": 73,
  "condition": "Clear",
  "humidity_percent": 78,
  "wind_kph": 59
}
```

**Error JSON (non-zero exit):**

```json
{"error": "<message>"}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Lambda error, AWS credentials not found, or invalid city |
| 2 | Usage error (missing required argument) |

## Agent Usage Pattern

```bash
# Explicit profile
weather-cli --profile columbia get --city Tokyo
weather-cli --profile columbia --json get --city Tokyo | jq '.temperature_c'

# Via environment variable (set once in shell or agent env)
export AWS_PROFILE=columbia
weather-cli get --city Tokyo
weather-cli --json get --city "New York" | jq '.temperature_c'
```
