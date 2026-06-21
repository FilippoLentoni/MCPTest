## Why

To expose a weather tool through the AgentCore MCP Gateway, we need a Lambda function that a coding agent can invoke to look up current weather conditions for any city. This is the first of two tool Lambdas that will back the gateway; without it the MCP endpoint has no tools to serve.

## What Changes

- New AWS Lambda function `weather-tool` that accepts a city name and returns current weather data by calling the wttr.in public API
- AgentCore Gateway tool registration that exposes the Lambda as an MCP-compatible tool with a typed JSON Schema input/output contract
- AWS SAM template for reproducible deployment to account `columbia` (169976659173)

## Capabilities

### New Capabilities

- `weather-tool`: Lambda function that takes a `city` string and returns current conditions (temperature, description, humidity, wind) for that city
- `agentcore-weather-registration`: Tool registration in the AgentCore Gateway that maps the `get_weather` tool name to the Lambda ARN with a typed input schema

### Modified Capabilities

<!-- None — this is a new capability -->

## Impact

- New Lambda function in `columbia` account, `us-east-1` region
- New SAM stack `weather-tool-stack`
- AgentCore Gateway gains one registered tool (`get_weather`)
- No breaking changes to existing resources
