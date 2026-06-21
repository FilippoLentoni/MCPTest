## 1. Update CDK Stack

- [x] 1.1 In `cdk/stacks/gateway_stack.py`, change `AuthorizerType` from `AWS_IAM` to `NONE`
- [x] 1.2 Run `cdk diff McpGatewayStack --profile columbia` and confirm only `AuthorizerType` changes

## 2. Deploy Gateway

- [x] 2.1 Run `cdk deploy McpGatewayStack --profile columbia` from `cdk/`
- [x] 2.2 After deploy, check CloudFormation outputs — note whether gateway ID changed or stayed the same
- [x] 2.3 If gateway ID changed: update `gateway_config.json` with new `gateway_id` and `mcp_endpoint_url`, then redeploy `RegisterWeatherToolStack`

## 3. Verify Gateway is Accessible Without Auth

- [x] 3.1 Run `curl -s -X POST <mcp_endpoint_url> -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 -m json.tool` — confirm HTTP 200 and `get_weather` appears in tool list

## 4. Register Gateway in Claude Code

- [x] 4.1 Remove stale `type: "aws"` entry from `.claude/settings.json` (delete `mcpServers` key and `enableAllProjectMcpServers`)
- [x] 4.2 Remove `.mcp.json` (or clear its `mcpServers` to `{}`)
- [x] 4.3 Run `claude mcp add agentcore-gateway <mcp_endpoint_url> --transport http --scope user`
- [x] 4.4 Run `claude mcp list` and confirm `agentcore-gateway` shows as connected (not "Skipped")

## 5. Verify End-to-End in Claude Code

- [x] 5.1 In a Claude Code session (VS Code or CLI), ask "what's the weather in Tokyo?" — confirm `get_weather` tool is invoked and returns structured weather data
- [x] 5.2 Run `/mcp` in CLI and confirm `agentcore-gateway` appears with status `connected`
