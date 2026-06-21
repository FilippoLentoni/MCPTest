## Context

Greenfield. No existing AgentCore resources in the `columbia` account. This change creates only the Gateway resource — it does not deploy any Lambda functions or register any tools. Tool Lambdas are created in `weather-lambda-tool` and `stock-lambda-tool`; registration happens in `register-tools`.

All AWS infrastructure in this project is deployed via AWS CDK (Python) so that stacks are fully reproducible, portable across accounts, and deployable without clicking in the console.

AWS AgentCore Gateway (part of Amazon Bedrock) exposes an MCP-compatible HTTPS endpoint. Claude Code connects to it as an MCP server and discovers/invokes any tools registered against it.

## Goals / Non-Goals

**Goals:**
- Gateway resource created via `cdk deploy` with no manual console steps
- MCP endpoint URL is known and reachable after deploy
- Gateway metadata saved in `gateway_config.json` (populated from CDK stack output) for other changes to consume
- Stack is portable: deploying to a different account only requires changing the CDK environment

**Non-Goals:**
- Any tool registration (separate change)
- VPC / private networking
- Custom domain name for the endpoint

## Decisions

### D1: AWS CDK (Python) for all infrastructure
All AWS resources in this project are deployed via CDK. No manual console clicks, no SAM, no raw CloudFormation files. This makes every deployment reproducible, diffable in git, and portable to any account by changing `env=`.

**Language chosen: Python.** The Lambda functions are also Python; using the same language for CDK keeps the project to a single toolchain.

**Alternatives considered:**
- AWS Console — not reproducible, not portable, blocked for this project
- SAM — Lambda-focused, no first-class support for AgentCore Gateway; mixing SAM + CDK adds toolchain complexity
- CDK TypeScript — better IDE support but introduces a second language; rejected for simplicity

### D2: Single CDK app, one stack per feature
All stacks live in one CDK app rooted at `cdk/`:

```
cdk/
├── app.py                   ← CDK app entry point; registers all stacks
├── requirements.txt
└── stacks/
    ├── gateway_stack.py     ← this change
    ├── weather_tool_stack.py    ← weather-lambda-tool change
    └── stock_tool_stack.py      ← stock-lambda-tool change
```

Each change adds one file under `cdk/stacks/` and registers it in `app.py`. Stacks can be deployed independently with `cdk deploy <StackName>`.

**Alternatives considered:**
- One CDK app per change — more isolation but makes cross-stack references (e.g. Lambda ARN → Gateway) harder; rejected

### D3: CDK environment pinned to columbia account
```python
env = cdk.Environment(account="169976659173", region="us-east-1")
```
Pinning the account and region means accidental deploys to the wrong account fail fast. To port to another account, change one line.

### D4: AgentCore Gateway via L1 CFN construct
AgentCore Gateway is a new service; CDK L2 constructs are not yet available. Use `cdk.CfnResource` with type `AWS::BedrockAgentCore::Gateway` until an L2 becomes available. If `aws_cdk.aws_bedrockagentcore.CfnGateway` is available in the installed CDK version, prefer that.

```python
gateway = cdk.CfnResource(
    self, "McpToolsGateway",
    type="AWS::BedrockAgentCore::Gateway",
    properties={
        "Name": "mcp-tools-gateway",
        "ProtocolType": "MCP",
        "AuthorizerType": "AWS_IAM",
    }
)
```

**Note:** Verify the exact CFN resource type and property names against the [CloudFormation resource spec](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_BedrockAgentCore.html) during implementation — new services sometimes ship CFN support under a slightly different namespace.

### D5: IAM authentication (SigV4)
Use IAM auth on the gateway. Claude Code supports IAM-signed MCP requests when the MCP server config uses `"type": "aws"`. This avoids managing API keys.

### D6: Gateway metadata in gateway_config.json via CfnOutput
Export `gateway_id` and `mcp_endpoint_url` as CDK stack outputs. After `cdk deploy`, a post-deploy script reads `cdk outputs --json` and writes `gateway_config.json` at repo root. Downstream changes read from this file.

```json
{
  "gateway_id": "<from stack output>",
  "mcp_endpoint_url": "<from stack output>",
  "region": "us-east-1",
  "account_id": "169976659173"
}
```

No sensitive values — gateway ID and endpoint URL are non-secret identifiers.

## Risks / Trade-offs

- **L1 CFN resource type name** — if the AgentCore CFN resource is not `AWS::BedrockAgentCore::Gateway`, `cdk synth` will succeed but `cdk deploy` will fail. Mitigate: verify the CFN type name against live AWS documentation before writing the stack.
- **CDK bootstrap required** — the `columbia` account must be bootstrapped (`cdk bootstrap aws://169976659173/us-east-1`) before first deploy. Document as a one-time prerequisite.
- **IAM credentials required locally** — developer needs valid AWS credentials for `columbia`. Document `aws configure --profile columbia` as a prerequisite.

## Open Questions

- Should a dedicated CDK IAM deployment role be created for CI/CD, or use personal credentials for this experiment? (Deferred — personal credentials for now.)
