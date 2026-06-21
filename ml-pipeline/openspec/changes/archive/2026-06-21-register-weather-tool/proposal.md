# Proposal: register-weather-tool

## What

Register the `weather-tool` Lambda as a `get_weather` MCP tool in the AgentCore Gateway, so that Claude Code can call it by name over the MCP endpoint.

## Why

The `weather-lambda-tool` change deployed the Lambda and the `agentcore-gateway` change deployed the Gateway, but the two are not connected. Until a `GatewayTarget` resource is created, the MCP endpoint returns an empty tool list and the Lambda is unreachable via MCP.

## Scope

One CDK stack — `RegisterWeatherToolStack` — that creates a single `AWS::BedrockAgentCore::GatewayTarget` resource wiring the `weather-tool` Lambda into the gateway as the `get_weather` tool.

No Lambda code changes. No gateway changes. No IAM additions (the gateway role already carries a `lambda:InvokeFunction` wildcard from the `agentcore-gateway` change).

## Out of scope

- Registering the stock-market Lambda (separate `register-stock-tool` change)
- Modifying the Lambda handler
- Any console work
