import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct


class MlPipelineStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "MlPipelineBucket",
            bucket_name=f"ml-pipeline-columbia-{self.account}",
            removal_policy=cdk.RemovalPolicy.RETAIN,
            versioned=False,
        )

        execution_role = iam.Role(
            self,
            "MlPipelineExecutionRole",
            role_name="ml-pipeline-execution-role",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
            ],
        )

        bucket.grant_read_write(execution_role)

        cdk.CfnOutput(self, "BucketName", value=bucket.bucket_name)
        cdk.CfnOutput(self, "ExecutionRoleArn", value=execution_role.role_arn)
