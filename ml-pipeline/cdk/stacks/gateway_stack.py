import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from constructs import Construct


class GatewayStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Service role — bedrock-agentcore assumes this to invoke targets
        gateway_role = iam.Role(
            self,
            "McpGatewayRole",
            role_name="mcp-tools-gateway-role",
            assumed_by=iam.ServicePrincipal(
                "bedrock-agentcore.amazonaws.com",
                conditions={
                    "StringEquals": {"aws:SourceAccount": self.account},
                },
            ),
            description="Service role for AgentCore MCP Gateway",
        )

        # Lambda invoke permission added here so the role is ready when
        # register-tools wires in the function ARNs. Scoped to this account.
        gateway_role.add_to_policy(
            iam.PolicyStatement(
                sid="AllowLambdaInvoke",
                actions=["lambda:InvokeFunction"],
                resources=[f"arn:aws:lambda:{self.region}:{self.account}:function:*"],
            )
        )

        # AgentCore Gateway — no L2 construct yet; using L1 CfnResource.
        # Type verified against CloudFormation resource spec June 2026.
        gateway = cdk.CfnResource(
            self,
            "McpToolsGateway",
            type="AWS::BedrockAgentCore::Gateway",
            properties={
                "Name": "mcp-tools-gateway",
                "AuthorizerType": "NONE",
                "ProtocolType": "MCP",
                "RoleArn": gateway_role.role_arn,
                "Description": "MCP entry point for AI agent tools",
            },
        )

        gateway.node.add_dependency(gateway_role)

        # Ref returns the GatewayIdentifier; GatewayUrl is the MCP endpoint.
        cdk.CfnOutput(self, "GatewayId", value=gateway.ref)
        cdk.CfnOutput(
            self,
            "McpEndpointUrl",
            value=gateway.get_att("GatewayUrl").to_string(),
        )
