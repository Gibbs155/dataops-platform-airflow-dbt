from aws_cdk import aws_ecr as ecr, Stack, RemovalPolicy
from constructs import Construct

class ECRStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.airflow_webserver_repo = ecr.Repository(
            self,
            "airflow_webserver_repo",
            repository_name="airflow_webserver_cdk",
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.airflow_scheduler_repo = ecr.Repository(
            self,
            "airflow_scheduler_repo",
            repository_name="airflow_scheduler_cdk",
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.airflow_worker_repo = ecr.Repository(
            self,
            "airflow_worker_repo",
            repository_name="airflow_worker_cdk",
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.dbt_repo = ecr.Repository(
            self,
            "dbt_ecr_repository",
            repository_name="dbt_cdk",
            removal_policy=RemovalPolicy.DESTROY,
        )