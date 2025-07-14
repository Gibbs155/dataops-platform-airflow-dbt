import os
from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as sm,
    Stack, RemovalPolicy, Duration
)
from stacks.vpc_stack import VpcStack
from constructs import Construct

class RDSStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: VpcStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.db_name = "airflow"
        self.rds_secret = sm.Secret(
            self,
            "airflow-rds",
            secret_name="airflow-rds-credentials",
            description="Credentials for RDS PostgreSQL.",
            generate_secret_string=sm.SecretStringGenerator(
                secret_string_template='{"username": "airflow"}',
                generate_string_key="password",
                password_length=16,
                exclude_characters='"@\\\\/.',
                exclude_punctuation=True,
            ),
        )
        credentials = rds.Credentials.from_secret(self.rds_secret)

        postgres = rds.DatabaseInstance(
            self,
            "RDS",
            credentials=credentials,
            instance_identifier="airflow-cdk",
            database_name=self.db_name,
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15  # Cambiado de VER_15_5 a VER_15_4
            ),
            vpc=vpc.instance,
            vpc_placement=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            port=5432,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,  # Cambiado de BURSTABLE2 a BURSTABLE3 (más actual)
                ec2.InstanceSize.MICRO,
            ),
            allocated_storage=20,
            security_groups=[vpc.postgres_sg],
            removal_policy=RemovalPolicy.DESTROY,
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self, "para-group-postgres", parameter_group_name="default.postgres15"
            ),
            deletion_protection=False,
        )

        self._instance = postgres

    @property
    def instance(self) -> rds.DatabaseInstance:
        return self._instance