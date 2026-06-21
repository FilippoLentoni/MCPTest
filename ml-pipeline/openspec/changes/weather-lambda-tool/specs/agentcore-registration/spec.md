## ADDED Requirements

### Requirement: Register the weather Lambda as an AgentCore Gateway tool
The system SHALL register the `weather-tool` Lambda as a tool named `get_weather` in the AgentCore Gateway so that MCP clients (including Claude Code via the MCP server config) can discover and invoke it.

#### Scenario: Tool appears in Gateway tool list
- **WHEN** the registration step completes
- **THEN** calling `aws bedrock-agentcore list-gateway-tools --gateway-id <id>` returns a tool entry with `name: get_weather`

#### Scenario: Tool schema is correct
- **WHEN** the tool is registered
- **THEN** the input schema for `get_weather` matches exactly:
  ```json
  {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "Name of the city to get weather for, e.g. 'London' or 'New York'"
      }
    },
    "required": ["city"]
  }
  ```

---

### Requirement: Claude Code agent can invoke get_weather via MCP
The system SHALL be verifiable end-to-end by a Claude Code agent connecting to the AgentCore Gateway MCP endpoint and successfully calling the weather tool.

#### Scenario: Agent invokes get_weather through MCP
- **WHEN** a Claude Code agent has the AgentCore Gateway configured as an MCP server
- **AND** the agent sends `get_weather(city="Paris")`
- **THEN** the agent receives a tool result containing weather data for Paris with temperature, condition, and humidity fields

#### Scenario: MCP server config for Claude Code
- **WHEN** the AgentCore Gateway endpoint URL is known
- **THEN** a developer can add it to their Claude Code MCP config (`~/.claude/mcp_servers.json` or `.claude/settings.json`) as:
  ```json
  {
    "mcpServers": {
      "agentcore-gateway": {
        "type": "url",
        "url": "<gateway-mcp-endpoint-url>"
      }
    }
  }
  ```
- **AND** running `/mcp` in Claude Code shows `agentcore-gateway` connected with `get_weather` listed as an available tool

---

### Requirement: Registration is reproducible via CLI script
The system SHALL include a shell script `scripts/register_tools.sh` that registers the weather tool in the Gateway using the AWS CLI. Running the script twice SHALL be idempotent (no duplicate registrations).

#### Scenario: Script runs successfully
- **WHEN** `bash scripts/register_tools.sh` is run with valid AWS credentials and `GATEWAY_ID` env var set
- **THEN** the script exits with code 0 and prints the registered tool ARN

#### Scenario: Idempotent re-run
- **WHEN** the script is run a second time
- **THEN** it detects the tool is already registered and skips creation (or updates in place), exits with code 0
