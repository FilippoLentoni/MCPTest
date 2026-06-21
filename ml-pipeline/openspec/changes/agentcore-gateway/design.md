## Context

Greenfield. No existing AgentCore resources in the `columbia` account. This change creates only the Gateway resource — it does not deploy any Lambda functions or register any tools. Tool Lambdas are created in `weather-lambda-tool` and `stock-lambda-tool`; registration happens in `register-tools`.

AWS AgentCore Gateway (part of Amazon Bedrock) exposes an MCP-compatible HTTPS endpoint. Claude Code can connect to it as an MCP server and discover/invoke any tools registered against it.

## Goals / Non-Goals

**Goals:**
- Gateway resource exists and is in `ACTIVE` state
- MCP endpoint URL is known and reachable
- Gateway metadata is saved in `gateway_config.json` for other changes to consume

**Non-Goals:**
- Any tool registration (separate change)
- VPC / private networking
- Custom domain name for the endpoint
- CloudFormation / CDK IaC for the gateway (manual creation for first iteration; can be codified later)

## Decisions

### D1: Create via AWS Console, not IaC
AgentCore Gateway is a new service with limited CloudFormation support at the time of writing. Creating it manually via the Bedrock console is the lowest-friction path.

**Alternatives considered:**
- AWS CDK with L1 CFN resource — requires keeping up with rapidly changing L1 schema; deferred to a future iteration
- AWS CLI (`aws bedrock-agentcore create-gateway`) — viable, but requires knowing all parameters upfront; console gives guided UX for first creation

### D2: Gateway name `mcp-tools-gateway`
Descriptive, scoped to this experiment. A single gateway can hold multiple tools, so it is shared across all tool registrations.

**Alternatives considered:**
- One gateway per tool — unnecessary overhead, more endpoints to manage

### D3: IAM authentication on the gateway
Use IAM auth (SigV4) rather than an API key. Claude Code supports IAM-signed MCP requests when the gateway is configured as `"type": "aws"` in the MCP server config.

**Alternatives considered:**
- API key auth — simpler to configure but requires rotating secrets; IAM is cleaner for AWS-native tooling

### D4: Record metadata in `gateway_config.json`
Save `gateway_id` and `mcp_endpoint_url` to a JSON file committed to the repo. This avoids copy-pasting between spec changes and gives the coding agent a single source of truth when implementing `register-tools`.

```json
{
  "gateway_id": "<to be filled after creation>",
  "mcp_endpoint_url": "<to be filled after creation>",
  "region": "us-east-1",
  "account_id": "169976659173"
}
```

No sensitive values — the gateway ID and endpoint URL are non-secret identifiers.

## Risks / Trade-offs

- **Manual creation is not reproducible by CI** — acceptable for an experiment; flag for the `agentcore-gateway` IaC change if this project moves to production.
- **IAM auth requires AWS credentials in Claude Code** — developer must have valid credentials for the `columbia` account in their local AWS config. Document the `aws configure --profile columbia` step.

## Open Questions

- Should Claude Code use a dedicated IAM role/user for gateway access, or the developer's personal credentials? (Deferred — use personal credentials for the experiment, create a dedicated role for any persistent deployment.)
