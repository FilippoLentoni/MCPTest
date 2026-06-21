# Design: register-weather-tool

## Decisions

### D1 — CDK `CfnResource` for `AWS::BedrockAgentCore::GatewayTarget`

No L2 construct exists for `BedrockAgentCore`. We use `cdk.CfnResource` with the verified CFN type, consistent with `agentcore-gateway`.

### D2 — Gateway ID read from `gateway_config.json` at synth time

The gateway was deployed by the `agentcore-gateway` change, which wrote `gateway_config.json` at the repo root. `RegisterWeatherToolStack` reads `gateway_config["gateway_id"]` at Python import time using `pathlib`. This avoids a CDK cross-stack reference and keeps the stacks independently deployable.

```python
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
_GATEWAY_ID = json.loads((_REPO_ROOT / "gateway_config.json").read_text())["gateway_id"]
```

### D3 — Lambda ARN imported by function name

The `weather-tool` Lambda is in the same account and region. CDK resolves the ARN from the function name at synth time:

```python
from aws_cdk import aws_lambda as lambda_

weather_fn = lambda_.Function.from_function_name(
    self, "WeatherToolRef", function_name="weather-tool"
)
```

No cross-stack exports needed.

### D4 — Tool schema defined inline (`InlinePayload`), not in S3

The schema is small (one tool, one parameter). Using `InlinePayload` keeps everything in the CDK stack with no S3 dependency.

### D5 — Single tool: `get_weather`, required string parameter `city`

```
ToolDefinition:
  Name: get_weather
  Description: Returns current weather conditions for a city (temperature, condition, humidity, wind speed)
  InputSchema:
    Type: object
    Properties:
      city:
        Type: string
        Description: Name of the city (e.g. "Tokyo", "New York")
    Required: [city]
```

### D6 — No new IAM resources

The gateway role (`McpGatewayStack`) already has `lambda:InvokeFunction` with a `*` resource. No additional role or resource-based policy is needed.

## CFN shape

```yaml
Type: AWS::BedrockAgentCore::GatewayTarget
Properties:
  GatewayIdentifier: <from gateway_config.json>
  Name: weather-tool-target
  Description: Routes get_weather MCP calls to the weather-tool Lambda
  TargetConfiguration:
    Mcp:
      Lambda:
        LambdaArn: <arn of weather-tool Lambda>
        ToolSchema:
          InlinePayload:
            - Name: get_weather
              Description: Returns current weather conditions for a city
              InputSchema:
                Type: object
                Properties:
                  city:
                    Type: string
                    Description: Name of the city
                Required:
                  - city
```
