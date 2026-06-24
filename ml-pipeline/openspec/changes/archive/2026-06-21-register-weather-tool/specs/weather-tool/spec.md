## ADDED Requirements

### Requirement: Weather tool is invocable via MCP through the AgentCore Gateway
The system SHALL allow a Claude Code session to call the weather tool by name over MCP — no direct Lambda invocation or IAM Lambda permissions required from the caller.

#### Scenario: Claude Code calls get_weather via MCP
- **WHEN** a Claude Code session has `agentcore-gateway` configured as an MCP server
- **AND** the user asks for the weather in any city (e.g. "what's the weather in Tokyo?")
- **THEN** Claude Code invokes the `get_weather` tool via the MCP endpoint
- **AND** the response contains a JSON object with `city`, `temperature_c`, `temperature_f`, `condition`, `humidity_percent`, `wind_kph`

#### Scenario: Tool schema exposed to MCP clients
- **WHEN** an MCP client calls `tools/list` on the gateway endpoint
- **THEN** the response includes a tool entry with name `get_weather`, a description, and an input schema requiring a `city` string parameter
