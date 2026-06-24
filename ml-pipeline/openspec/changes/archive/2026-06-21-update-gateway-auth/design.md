## Context

The AgentCore Gateway is deployed with `AuthorizerType: AWS_IAM`, which requires SigV4 request signing. Claude Code 2.1.185's MCP client does not support `type: "aws"` (SigV4) — the server is silently skipped with "unknown MCP server type". The AWS quick-start guide uses `AuthorizerType: NONE` for development. This is a one-property change to the CDK stack followed by a `claude mcp add` command.

## Goals / Non-Goals

**Goals:**
- Change gateway inbound auth to `NONE` so any HTTP client (including Claude Code's MCP client) can connect without signing
- Register the gateway in Claude Code via `claude mcp add --transport http` (global scope, picked up by VS Code extension)
- Clean up the now-invalid `type: "aws"` entries from `.claude/settings.json` and `.mcp.json`

**Non-Goals:**
- Production-grade auth (deferred to a future `add-gateway-jwt-auth` change using Cognito/OIDC)
- Any changes to Lambda code, GatewayTarget registration, or tool schema

## Decisions

### D1 — `AuthorizerType: NONE` (not `CUSTOM_JWT`)

`CUSTOM_JWT` requires setting up a Cognito user pool, client credentials, and OAuth discovery URL — significant infrastructure for a dev experiment. `NONE` removes the auth layer entirely and is the AWS-recommended path for local development and proof-of-concept work. The gateway is in a private AWS account with no sensitive data.

### D2 — `claude mcp add --scope user` for global registration

Using `--scope user` writes to `~/.claude/mcp.json` (the global user-level MCP config), which is read by both the CLI and the VS Code extension. Project-scope (`.mcp.json`) requires explicit trust approval; user-scope is always active. This avoids the trust-prompt issue entirely.

### D3 — Keep `AuthorizerType` as a named CDK variable

The change is one line in `gateway_stack.py`. No abstraction needed; the property stays inline in the `CfnResource` properties dict.

### D4 — Check if CloudFormation can update `AuthorizerType` in place

If CFN supports in-place update of `AuthorizerType`, the gateway ID stays the same and `gateway_config.json` does not change. If CFN forces replacement, the gateway gets a new ID and `gateway_config.json` must be updated, followed by a redeploy of `RegisterWeatherToolStack`. Verify after `cdk deploy`.

## Risks / Trade-offs

- **[Risk] Gateway is open to any caller** → Acceptable for a dev experiment in a private account with non-sensitive weather data. Not acceptable for production.
- **[Risk] CFN replacement changes gateway ID** → If it does, `RegisterWeatherToolStack` must be redeployed with the new `gateway_config.json`. Mitigated by checking outputs after deploy.
- **[Risk] Existing `type: "aws"` entries cause confusion** → Clean up both `.claude/settings.json` and `.mcp.json` immediately after the deploy.
