## ADDED Requirements

### Requirement: AgentCore Gateway resource exists and is active
The system SHALL have an AgentCore Gateway resource in the `columbia` AWS account (169976659173), region `us-east-1`, in `ACTIVE` state.

#### Scenario: Gateway is active
- **WHEN** a developer runs `aws bedrock-agentcore get-gateway --gateway-id <id> --region us-east-1`
- **THEN** the response contains `"status": "ACTIVE"` and a non-empty `endpointUrl`

---

### Requirement: Gateway metadata is recorded in gateway_config.json
The system SHALL have a `gateway_config.json` file at the repo root containing the gateway ID, MCP endpoint URL, region, and account ID so that downstream changes (`register-tools`) can reference it without manual lookup.

#### Scenario: Config file is present and complete
- **WHEN** a developer opens `gateway_config.json`
- **THEN** all four fields are populated: `gateway_id`, `mcp_endpoint_url`, `region`, `account_id`
- **AND** `mcp_endpoint_url` is an HTTPS URL ending in `/mcp`

---

### Requirement: Claude Code can connect to the gateway as an MCP server
The system SHALL be verifiable by adding the gateway to Claude Code's MCP server config and confirming it shows as connected (even with no tools registered yet).

#### Scenario: Empty gateway connects successfully
- **WHEN** the following entry is added to Claude Code MCP config:
  ```json
  {
    "mcpServers": {
      "agentcore-gateway": {
        "type": "aws",
        "url": "<mcp_endpoint_url from gateway_config.json>",
        "region": "us-east-1"
      }
    }
  }
  ```
- **AND** the developer has valid IAM credentials for the `columbia` account
- **THEN** running `/mcp` in a Claude Code session shows `agentcore-gateway` with status `connected`
- **AND** the tool list is empty (no tools registered yet — expected at this stage)
