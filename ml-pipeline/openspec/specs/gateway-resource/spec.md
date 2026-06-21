# Gateway Resource Spec

## Requirements

### Requirement: AgentCore Gateway deployed via CDK with no manual steps
The system SHALL deploy the AgentCore Gateway resource by running `cdk deploy` from the `cdk/` directory. No AWS Console interaction SHALL be required. The stack SHALL be re-deployable from a clean checkout on any machine with valid AWS credentials for the target account.

#### Scenario: Fresh deploy from a clean checkout
- **WHEN** a developer clones the repo, installs CDK dependencies, and runs `cdk deploy McpGatewayStack --profile columbia`
- **THEN** the CloudFormation stack `McpGatewayStack` is created in account `169976659173`, region `us-east-1`
- **AND** the stack reaches `CREATE_COMPLETE` with no manual intervention

#### Scenario: Deploy to a different account
- **WHEN** the `account` value in `GatewayStack`'s `cdk.Environment(...)` is changed to a different account ID
- **AND** `cdk deploy` is run with credentials for that account
- **THEN** an identical gateway is created in that account — no other code changes required

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

### Requirement: Claude Code connects to the gateway via MCP
The system SHALL be verifiable by adding the gateway to Claude Code's MCP server config and confirming it connects successfully.

#### Scenario: Empty gateway connects
- **WHEN** the MCP config entry is added with `"type": "aws"` and the URL from `gateway_config.json`
- **AND** the developer has valid IAM credentials for the `columbia` account
- **THEN** `/mcp` in a Claude Code session shows `agentcore-gateway` as `connected`
- **AND** the tool list is empty (expected — no tools registered yet)
