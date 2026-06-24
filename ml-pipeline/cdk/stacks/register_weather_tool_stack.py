import json
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_lambda as lambda_
from constructs import Construct

_REPO_ROOT = Path(__file__).parent.parent.parent
_GATEWAY_ID = json.loads((_REPO_ROOT / "gateway_config.json").read_text())["gateway_id"]
_WEATHER_LAMBDA_ARN = "arn:aws:lambda:us-east-1:169976659173:function:weather-tool"


class RegisterWeatherToolStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        target = cdk.CfnResource(
            self,
            "WeatherToolTarget",
            type="AWS::BedrockAgentCore::GatewayTarget",
            properties={
                "GatewayIdentifier": _GATEWAY_ID,
                "Name": "weather-tool-target",
                "Description": "Routes get_weather MCP calls to the weather-tool Lambda",
                "CredentialProviderConfigurations": [
                    {"CredentialProviderType": "GATEWAY_IAM_ROLE"}
                ],
                "TargetConfiguration": {
                    "Mcp": {
                        "Lambda": {
                            "LambdaArn": _WEATHER_LAMBDA_ARN,
                            "ToolSchema": {
                                "InlinePayload": [
                                    {
                                        "Name": "get_weather",
                                        "Description": "Returns current weather conditions for a city (temperature, condition, humidity, wind speed)",
                                        "InputSchema": {
                                            "Type": "object",
                                            "Properties": {
                                                "city": {
                                                    "Type": "string",
                                                    "Description": "Name of the city (e.g. Tokyo, New York)",
                                                }
                                            },
                                            "Required": ["city"],
                                        },
                                    }
                                ]
                            },
                        }
                    }
                },
            },
        )

        cdk.CfnOutput(
            self,
            "WeatherToolTargetId",
            value=target.get_att("TargetId").to_string(),
        )
