import aws_cdk as cdk
from stacks.gateway_stack import GatewayStack
from stacks.register_weather_tool_stack import RegisterWeatherToolStack
from stacks.weather_tool_stack import WeatherToolStack

app = cdk.App()

_ENV = cdk.Environment(account="169976659173", region="us-east-1")

GatewayStack(app, "McpGatewayStack", env=_ENV)
WeatherToolStack(app, "WeatherToolStack", env=_ENV)
RegisterWeatherToolStack(app, "RegisterWeatherToolStack", env=_ENV)

app.synth()
