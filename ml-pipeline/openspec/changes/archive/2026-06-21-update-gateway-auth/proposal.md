## Why

Claude Code 2.1.185 rejects `type: "aws"` MCP server configs with "unknown MCP server type" — SigV4/IAM auth is not supported by the current MCP client layer. The gateway must use `AuthorizerType: NONE` so Claude Code can connect over plain HTTP, which is the approach recommended by the AWS quick-start guide for development.

## What Changes

- `cdk/stacks/gateway_stack.py`: change `AuthorizerType` from `AWS_IAM` to `NONE`
- Redeploy `McpGatewayStack` to `columbia` (169976659173), `us-east-1`
- Replace `type: "aws"` MCP config in `.claude/settings.json` and `.mcp.json` with a plain `--transport http` entry registered via `claude mcp add`
- Update `gateway_config.json` if gateway ID changes after redeploy

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `gateway-resource`: inbound auth requirement changes from `AWS_IAM` (SigV4) to `NONE`; Claude Code connection method changes from `type: "aws"` settings entry to `claude mcp add --transport http`

## Impact

- `cdk/stacks/gateway_stack.py` — one-line change to `AuthorizerType`
- `McpGatewayStack` CloudFormation stack — in-place update or replacement
- `.claude/settings.json` and `.mcp.json` — MCP server config entries updated
- `gateway_config.json` — may need refresh if gateway ID changes
- `register-weather-tool` change — no code changes needed; `RegisterWeatherToolStack` uses `GatewayIdentifier` from `gateway_config.json` and is unaffected by auth type
