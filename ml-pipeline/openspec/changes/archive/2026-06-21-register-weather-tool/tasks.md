# Tasks: register-weather-tool

## 1. CDK Stack

- [x] 1.1 Create `cdk/stacks/register_weather_tool_stack.py` with `RegisterWeatherToolStack` extending `cdk.Stack`
- [x] 1.2 Read gateway ID from `gateway_config.json` at import time (see D2 in design.md)
- [x] 1.3 Import the Lambda using `lambda_.Function.from_function_name(self, "WeatherToolRef", function_name="weather-tool")` (see D3)
- [x] 1.4 Create `cdk.CfnResource` with type `AWS::BedrockAgentCore::GatewayTarget` using the CFN shape from design.md (D1, D4, D5)
- [x] 1.5 Add a `CfnOutput` for the target ID: `{"Fn::GetAtt": ["WeatherToolTarget", "TargetId"]}`
- [x] 1.6 Register `RegisterWeatherToolStack` in `cdk/app.py`

## 2. Synthesise

- [x] 2.1 From the `cdk/` directory run:
  ```bash
  cdk synth RegisterWeatherToolStack --app ".venv/bin/python app.py"
  ```
  Confirm the synthesised template contains `AWS::BedrockAgentCore::GatewayTarget` with `GatewayIdentifier`, `LambdaArn`, and `InlinePayload` set correctly.

## 3. Deploy

- [x] 3.1 Deploy:
  ```bash
  cdk deploy RegisterWeatherToolStack --profile columbia --app ".venv/bin/python app.py" --require-approval never
  ```
  Confirm the stack reaches `CREATE_COMPLETE` and CDK prints the `WeatherToolTargetId` output.

## 4. Verify registration

- [x] 4.1 Confirm the target status is `READY` via AWS CLI:
  ```bash
  aws bedrock-agentcore-control get-gateway-target \
    --gateway-identifier <gateway_id> \
    --target-id <target_id> \
    --region us-east-1 \
    --profile columbia
  ```
- [x] 4.2 Target ID recorded: `OV6VT8VZG8`
- [x] 4.3 Restart Claude Code (or run `/mcp` in a new session) and confirm `agentcore-gateway` lists `get_weather` as an available tool.
- [x] 4.4 Call the tool from Claude Code: ask "what's the weather in Tokyo?" and confirm a structured response is returned.
