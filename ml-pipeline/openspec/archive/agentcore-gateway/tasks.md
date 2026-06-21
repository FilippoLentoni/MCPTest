## 0. Prerequisites (one-time setup)

- [x] 0.1 Install CDK CLI: `npm install -g aws-cdk` and confirm `cdk --version` ≥ 2.x
- [x] 0.2 Configure AWS credentials for the `columbia` account:
  ```bash
  aws configure --profile columbia
  # or SSO: aws sso login --profile columbia
  ```
- [x] 0.3 Bootstrap the `columbia` account for CDK (one-time per account/region):
  ```bash
  cdk bootstrap aws://169976659173/us-east-1 --profile columbia
  ```
  Confirm the bootstrap stack reaches `CREATE_COMPLETE`.

## 1. CDK Project Structure

- [x] 1.1 Create the `cdk/` directory at repo root
- [x] 1.2 Create `cdk/requirements.txt`
- [x] 1.3 Create `cdk/app.py` — CDK app entry point
- [x] 1.4 Create `cdk/stacks/__init__.py` (empty)
- [x] 1.5 Create a Python virtual environment and install CDK dependencies

## 2. Gateway Stack (`cdk/stacks/gateway_stack.py`)

- [x] 2.1 Create `cdk/stacks/gateway_stack.py` with a `GatewayStack` class extending `cdk.Stack`
- [x] 2.2 CFN type confirmed as `AWS::BedrockAgentCore::Gateway`. No CDK L2 available; using `cdk.CfnResource`. GetAtt attribute is `GatewayUrl` (not `EndpointUrl`). Status value is `READY` (not `ACTIVE`). CLI service name is `bedrock-agentcore-control`.
- [x] 2.3 Gateway resource defined with `AuthorizerType: AWS_IAM`, `ProtocolType: MCP`, `RoleArn` from a CDK-managed IAM role
- [x] 2.4 CDK outputs added: `GatewayId` (gateway.ref) and `McpEndpointUrl` (gateway.get_att("GatewayUrl"))

## 3. Synthesise and Verify

- [x] 3.1 `cdk synth McpGatewayStack` — template contains IAM role, IAM policy, gateway resource, and two outputs
- [x] 3.2 Template reviewed — `Type: AWS::BedrockAgentCore::Gateway` with correct properties

## 4. Deploy

- [x] 4.1 `cdk deploy McpGatewayStack --profile columbia` — stack reached `CREATE_COMPLETE` in ~53s
- [x] 4.2 Outputs:
  - `GatewayId = mcp-tools-gateway-v5vpj8g3tk`
  - `McpEndpointUrl = https://mcp-tools-gateway-v5vpj8g3tk.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp`

## 5. Write gateway_config.json

- [x] 5.1 Stack outputs captured from CDK deploy output
- [x] 5.2 `gateway_config.json` created at repo root with live values
- [ ] 5.3 Commit `gateway_config.json` and CDK files

## 6. Verify Gateway via CLI

- [x] 6.1 Confirm the gateway is ready:
  ```bash
  aws bedrock-agentcore-control get-gateway \
    --gateway-identifier $(jq -r .gateway_id gateway_config.json) \
    --region us-east-1 \
    --profile columbia
  ```
  Response must contain `"status": "READY"`. Note: the AWS CLI service name is `bedrock-agentcore-control` (control plane), not `bedrock-agentcore` (data plane).

## 7. Verify Claude Code Connects

- [x] 7.1 `.claude/settings.json` written to repo root with `agentcore-gateway` MCP server entry (type: aws, IAM auth)
- [ ] 7.2 Start a new Claude Code session and run `/mcp`
- [ ] 7.3 Confirm `agentcore-gateway` shows status `connected` with an empty tool list — this is the acceptance criterion for this change
