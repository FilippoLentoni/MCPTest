from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_lambda as lambda_
from constructs import Construct

_REPO_ROOT = Path(__file__).parent.parent.parent


class WeatherToolStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        weather_fn = lambda_.Function(
            self,
            "WeatherTool",
            function_name="weather-tool",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(str(_REPO_ROOT / "src" / "weather_tool")),
            timeout=cdk.Duration.seconds(30),
            memory_size=128,
            description="Returns current weather for a given city via wttr.in",
        )

        cdk.CfnOutput(self, "WeatherToolArn", value=weather_fn.function_arn)
