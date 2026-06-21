## 0. Prerequisites (one-time setup)

- [ ] 0.1 Install CDK CLI: `npm install -g aws-cdk` and confirm `cdk --version` ≥ 2.x
- [ ] 0.2 Configure AWS credentials for the `columbia` account:
  ```bash
  aws configure --profile columbia
  # or SSO: aws sso login --profile columbia
  ```
- [ ] 0.3 Bootstrap the `columbia` account for CDK (one-time per account/region):
  ```bash
  cdk bootstrap aws://169976659173/us-east-1 --profile columbia
  ```
  Confirm the bootstrap stack reaches `CREATE_COMPLETE`.

## 1. CDK Project Structure

- [ ] 1.1 Create the `cdk/` directory at repo root
- [ ] 1.2 Create `cdk/requirements.txt`:
  ```
  aws-cdk-lib>=2.100.0
  constructs>=10.0.0
  ```
- [ ] 1.3 Create `cdk/app.py` — CDK app entry point:
  ```python
  import aws_cdk as cdk
  from stacks.gateway_stack import GatewayStack

  app = cdk.App()

  GatewayStack(
      app, "McpGatewayStack",
      env=cdk.Environment(account="169976659173", region="us-east-1"),
  )

  app.synth()
  ```
- [ ] 1.4 Create `cdk/stacks/__init__.py` (empty)
- [ ] 1.5 Create a Python virtual environment and install CDK dependencies:
  ```bash
  cd cdk
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

## 2. Gateway Stack (`cdk/stacks/gateway_stack.py`)

- [ ] 2.1 Create `cdk/stacks/gateway_stack.py` with a `GatewayStack` class extending `cdk.Stack`
- [ ] 2.2 Before writing the resource, confirm the CloudFormation resource type for AgentCore Gateway by checking:
  - AWS CloudFormation resource spec: search for `BedrockAgentCore` at https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html
  - Or run: `aws cloudformation describe-type --type-name AWS::BedrockAgentCore::Gateway --region us-east-1`
  - If `aws_cdk.aws_bedrockagentcore.CfnGateway` exists in the installed CDK version, use it; otherwise use `cdk.CfnResource`
- [ ] 2.3 Define the gateway resource using the verified CFN type:
  ```python
  gateway = cdk.CfnResource(
      self, "McpToolsGateway",
      type="AWS::BedrockAgentCore::Gateway",   # verify exact type name
      properties={
          "Name": "mcp-tools-gateway",
          "ProtocolType": "MCP",
          "AuthorizerType": "AWS_IAM",
      }
  )
  ```
- [ ] 2.4 Add CDK stack outputs for `GatewayId` and `McpEndpointUrl`:
  ```python
  cdk.CfnOutput(self, "GatewayId", value=gateway.ref)
  cdk.CfnOutput(self, "McpEndpointUrl", value=gateway.get_att("EndpointUrl").to_string())
  ```
  Adjust the `get_att` attribute name to match the actual CFN output attribute name from step 2.2.

## 3. Synthesise and Verify

- [ ] 3.1 From the `cdk/` directory, run:
  ```bash
  cdk synth McpGatewayStack
  ```
  Confirm the output CloudFormation template contains the gateway resource and two outputs.
- [ ] 3.2 Review the synthesised template in `cdk.out/McpGatewayStack.template.json` — verify `Type` and `Properties` match the CFN spec.

## 4. Deploy

- [ ] 4.1 Deploy the stack:
  ```bash
  cdk deploy McpGatewayStack --profile columbia
  ```
  Confirm the stack reaches `CREATE_COMPLETE` and CDK prints the two output values.
- [ ] 4.2 Note the printed `GatewayId` and `McpEndpointUrl` output values.

## 5. Write gateway_config.json

- [ ] 5.1 Capture the stack outputs programmatically:
  ```bash
  aws cloudformation describe-stacks \
    --stack-name McpGatewayStack \
    --region us-east-1 \
    --profile columbia \
    --query "Stacks[0].Outputs" \
    --output json
  ```
- [ ] 5.2 Create `gateway_config.json` at repo root:
  ```json
  {
    "gateway_id": "<GatewayId output value>",
    "mcp_endpoint_url": "<McpEndpointUrl output value>",
    "region": "us-east-1",
    "account_id": "169976659173"
  }
  ```
- [ ] 5.3 Commit `gateway_config.json`: `git add gateway_config.json && git commit -m "config: add AgentCore gateway metadata"`

## 6. Verify Gateway via CLI

- [ ] 6.1 Confirm the gateway is active:
  ```bash
  aws bedrock-agentcore get-gateway \
    --gateway-id $(jq -r .gateway_id gateway_config.json) \
    --region us-east-1 \
    --profile columbia
  ```
  Response must contain `"status": "ACTIVE"`.

## 7. Verify Claude Code Connects

- [ ] 7.1 Add the gateway to Claude Code MCP config (`.claude/settings.json` in repo or `~/.claude/settings.json`):
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
- [ ] 7.2 Start a new Claude Code session and run `/mcp`
- [ ] 7.3 Confirm `agentcore-gateway` shows status `connected` with an empty tool list — this is the acceptance criterion for this change
