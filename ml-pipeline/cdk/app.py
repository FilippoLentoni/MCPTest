import aws_cdk as cdk
from stacks.gateway_stack import GatewayStack

app = cdk.App()

GatewayStack(
    app,
    "McpGatewayStack",
    env=cdk.Environment(account="169976659173", region="us-east-1"),
)

app.synth()
