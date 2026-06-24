# Gateway Resource Spec

## Requirements

### Requirement: AgentCore Gateway deployed via CDK with no manual steps
The system SHALL deploy the AgentCore Gateway resource by running `cdk deploy` from the `cdk/` directory. No AWS Console interaction SHALL be required. The stack SHALL be re-deployable from a clean checkout on any machine with valid AWS credentials for the target account.

#### Scenario: Fresh deploy from a clean checkout
- **WHEN** a developer clones the repo, installs CDK dependencies, and runs `cdk deploy McpGatewayStack --profile columbia`
- **THEN** the CloudFormation stack `McpGatewayStack` is created in account `169976659173`, region `us-east-1`
- **AND** the stack reaches `CREATE_COMPLETE` (or `UPDATE_COMPLETE`) with no manual intervention

#### Scenario: Deploy to a different account
- **WHEN** the `account` value in `GatewayStack`'s `cdk.Environment(...)` is changed to a different account ID
- **AND** `cdk deploy` is run with credentials for that account
- **THEN** an identical gateway is created in that account — no other code changes required

---

### Requirement: Gateway uses no inbound authentication
The system SHALL configure the AgentCore Gateway with `AuthorizerType: NONE` so that any HTTP client can connect without SigV4 signing or Bearer tokens.

#### Scenario: Unauthenticated MCP client can list tools
- **WHEN** an HTTP client sends a POST to the gateway MCP endpoint with body `{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}`
- **AND** no `Authorization` header is present
- **THEN** the gateway returns the list of registered tools with HTTP 200

---

### Requirement: Gateway is ready after deploy
The system SHALL result in an AgentCore Gateway in `READY` state after `cdk deploy` completes.

#### Scenario: Gateway is ready
- **WHEN** `aws bedrock-agentcore-control get-gateway --gateway-identifier <id>` is run after deploy
- **THEN** the response contains `"status": "READY"` and a non-empty `gatewayUrl`

---

### Requirement: Gateway metadata recorded in gateway_config.json
The system SHALL have a `gateway_config.json` file at repo root, populated from CDK stack outputs, containing `gateway_id`, `mcp_endpoint_url`, `region`, and `account_id`.

#### Scenario: Config file is complete
- **WHEN** `gateway_config.json` is read after deploy
- **THEN** all four fields are non-empty strings
- **AND** `mcp_endpoint_url` is an HTTPS URL

---

### Requirement: Gateway has a registered get_weather MCP tool
The system SHALL have a `AWS::BedrockAgentCore::GatewayTarget` resource deployed in `RegisterWeatherToolStack` that registers the `weather-tool` Lambda as the `get_weather` MCP tool on the gateway.

#### Scenario: GatewayTarget is READY
- **WHEN** `aws bedrock-agentcore-control get-gateway-target --gateway-identifier <id> --target-id <id>` is run after deploy
- **THEN** the response contains `"status": "READY"`

#### Scenario: GatewayTarget routes to the weather Lambda
- **WHEN** an MCP client calls the `get_weather` tool on the gateway
- **THEN** the gateway invokes `arn:aws:lambda:us-east-1:169976659173:function:weather-tool` with the tool input as the event payload

---

### Requirement: Claude Code connects to the gateway via MCP
The system SHALL be verifiable by connecting Claude Code to the gateway MCP endpoint using `claude mcp add --transport http` and confirming the `get_weather` tool is available.

#### Scenario: Gateway connects with get_weather tool listed
- **WHEN** the MCP server is registered with `claude mcp add agentcore-gateway <url> --transport http --scope user`
- **AND** the developer has an active Claude Code session (CLI or VS Code extension)
- **THEN** `/mcp` shows `agentcore-gateway` as `connected`
- **AND** the tool list contains `get_weather`

#### Scenario: Claude Code can invoke get_weather via MCP
- **WHEN** the user asks "what's the weather in Tokyo?" in a Claude Code session
- **THEN** Claude Code invokes the `get_weather` MCP tool
- **AND** the response contains `city`, `temperature_c`, `condition`, `humidity_percent`, and `wind_kph`
