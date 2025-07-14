import os
from aws_cdk import (
    Stack, RemovalPolicy,
    aws_ecs as ecs,
)
from types import SimpleNamespace
from stacks.airflow_cluster_stack import AirflowClusterStack
from stacks.ecr_stack import ECRStack
from stacks.redshift_cluster_stack import RedshiftClusterStack
from typing_extensions import TypedDict
from constructs import Construct

props_type = TypedDict(
    "props_type",
    {
        "airflow_cluster": AirflowClusterStack,
        "ecr": ECRStack,
        "redshift": RedshiftClusterStack,
    },
)


class DBT(Stack):
    def __init__(
        self, scope: Construct, id: str, props: props_type, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        ns = SimpleNamespace(**props)

        bucket_name = os.environ.get("BUCKET_NAME")
        dbt_task = ecs.FargateTaskDefinition(
            self,
            "dbt-cdk",
            family="dbt-cdk",
            cpu=512,
            memory_limit_mib=1024,
            task_role=ns.airflow_cluster.airflow_task_role,
            execution_role=ns.airflow_cluster.task_execution_role,
        )
        dbt_task.add_container(
            "dbt-cdk-container",
            image=ecs.ContainerImage.from_ecr_repository(
                ns.ecr.dbt_repo,
                os.environ.get("IMAGE_TAG", "latest"),
            ),
            logging=ecs.AwsLogDriver(
                stream_prefix="ecs", log_group=ns.airflow_cluster.dbt_log_group
            ),
            environment={
                "BUCKET_NAME": bucket_name,
                # Corregido: usar attr_endpoint en lugar de cluster_endpoint.hostname
                "REDSHIFT_HOST": ns.redshift.instance.attr_endpoint,
            },
            secrets={
                "REDSHIFT_USER": ecs.Secret.from_secrets_manager(
                    ns.redshift.redshift_secret, field="username"
                ),
                "REDSHIFT_PASSWORD": ecs.Secret.from_secrets_manager(
                    ns.redshift.redshift_secret, field="password"
                ),
            },
        )