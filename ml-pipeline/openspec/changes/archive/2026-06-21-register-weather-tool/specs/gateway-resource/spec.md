## ADDED Requirements

### Requirement: Gateway has a registered get_weather MCP tool
The system SHALL have a `AWS::BedrockAgentCore::GatewayTarget` resource deployed in `RegisterWeatherToolStack` that registers the `weather-tool` Lambda as the `get_weather` MCP tool on the gateway.

#### Scenario: GatewayTarget is READY
- **WHEN** `aws bedrock-agentcore-control get-gateway-target --gateway-identifier <id> --target-id <id>` is run after deploy
- **THEN** the response contains `"status": "READY"`

#### Scenario: GatewayTarget routes to the weather Lambda
- **WHEN** an MCP client calls the `get_weather` tool on the gateway
- **THEN** the gateway invokes `arn:aws:lambda:us-east-1:169976659173:function:weather-tool` with the tool input as the event payload

---

## MODIFIED Requirements

### Requirement: Claude Code connects to the gateway via MCP
*(replaces the "Empty gateway connects" scenario — tool list is no longer empty)*

#### Scenario: Gateway connects with get_weather tool listed
- **WHEN** the MCP config entry is present with `"type": "aws"` and the URL from `gateway_config.json`
- **AND** the developer has valid IAM credentials for the `columbia` account
- **THEN** `/mcp` in a Claude Code session shows `agentcore-gateway` as `connected`
- **AND** the tool list contains `get_weather`
