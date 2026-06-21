# Spec: tool-registration (register-weather-tool)

## Capability

The AgentCore Gateway exposes a `get_weather` tool over MCP. Claude Code can discover and invoke it without any manual AWS console interaction.

## Requirements

### REQ-01 — GatewayTarget resource exists

A `AWS::BedrockAgentCore::GatewayTarget` resource must exist in the `columbia` account (`169976659173`), `us-east-1`, associated with gateway `mcp-tools-gateway-v5vpj8g3tk`.

### REQ-02 — Tool name and schema

The target must declare exactly one tool:

| Field | Value |
|---|---|
| Name | `get_weather` |
| Description | "Returns current weather conditions for a city (temperature, condition, humidity, wind speed)" |
| Input parameter | `city` (string, required) |
| Input schema type | `object` |

### REQ-03 — Lambda routing

The target must route `get_weather` calls to `arn:aws:lambda:us-east-1:169976659173:function:weather-tool`.

### REQ-04 — Target status

After deployment the target status reported by `bedrock-agentcore-control get-gateway-target` must be `READY`.

### REQ-05 — End-to-end MCP call

A Claude Code session with the `agentcore-gateway` MCP server configured must be able to list `get_weather` and receive a valid JSON response containing `city`, `temperature_c`, `temperature_f`, `condition`, `humidity_percent`, and `wind_kph` when the tool is invoked with any valid city name.

### REQ-06 — CDK only

All infrastructure is managed by CDK. No manual AWS console actions are performed.
