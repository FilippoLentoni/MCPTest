## 1. Create the Gateway via AWS Console

- [ ] 1.1 Open the AWS Console in account `columbia` (169976659173), switch to region `us-east-1`
- [ ] 1.2 Navigate to **Amazon Bedrock → AgentCore → Gateways → Create Gateway**
- [ ] 1.3 Set gateway name to `mcp-tools-gateway`
- [ ] 1.4 Set authentication to **IAM** (SigV4)
- [ ] 1.5 Leave all other settings as defaults and click **Create**
- [ ] 1.6 Wait for the gateway to reach `ACTIVE` status (usually < 2 minutes)

## 2. Record Gateway Metadata

- [ ] 2.1 On the gateway detail page, copy the **Gateway ID** (format: `gwy-xxxxxxxxxxxx`)
- [ ] 2.2 Copy the **MCP Endpoint URL** (format: `https://<id>.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp`)
- [ ] 2.3 Create `gateway_config.json` at the repo root with the following content (fill in the real values):
  ```json
  {
    "gateway_id": "<gateway-id>",
    "mcp_endpoint_url": "<mcp-endpoint-url>",
    "region": "us-east-1",
    "account_id": "169976659173"
  }
  ```
- [ ] 2.4 Commit `gateway_config.json`: `git add gateway_config.json && git commit -m "config: add AgentCore gateway metadata"`

## 3. Verify Gateway is Reachable via CLI

- [ ] 3.1 Run:
  ```bash
  aws bedrock-agentcore get-gateway \
    --gateway-id $(jq -r .gateway_id gateway_config.json) \
    --region us-east-1
  ```
  Confirm the response contains `"status": "ACTIVE"`.

## 4. Verify Claude Code Can Connect

- [ ] 4.1 Ensure you have IAM credentials for the `columbia` account configured locally:
  ```bash
  aws configure --profile columbia
  # or use AWS SSO: aws sso login --profile columbia
  ```
- [ ] 4.2 Add the gateway to Claude Code MCP config (`~/.claude/settings.json` or `.claude/settings.json` in the repo):
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
- [ ] 4.3 Start a new Claude Code session and run `/mcp`
- [ ] 4.4 Confirm `agentcore-gateway` appears with status `connected` and an empty tool list
- [ ] 4.5 Screenshot or note the `/mcp` output as proof of connectivity — this is the acceptance criterion for this change
