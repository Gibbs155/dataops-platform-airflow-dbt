import os
from aws_cdk import (
    aws_redshift as redshift,
    aws_secretsmanager as sm,
    aws_ec2 as ec2,
    aws_iam as iam,
    Stack, RemovalPolicy
)
from stacks.vpc_stack import VpcStack
from constructs import Construct

class RedshiftClusterStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: VpcStack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Crear subnet group para Redshift
        subnet_group = redshift.CfnClusterSubnetGroup(
            self,
            id="RedshiftSubnetGroup", 
            description="Redshift private subnet group",
            subnet_ids=vpc.get_vpc_private_subnet_ids,  
        )

        # Crear secret para credenciales de Redshift
        self.redshift_secret = sm.Secret(
            self,
            "redshift-credentials",
            secret_name="redshift-credentials",
            description="Credentials for Amazon Redshift cluster.",
            generate_secret_string=sm.SecretStringGenerator(
                secret_string_template='{"username": "redshift-user"}',
                generate_string_key="password",
                password_length=32,
                exclude_characters='"@\\\\/',
                exclude_punctuation=True,
            ),
        )

        # Crear rol IAM para acceso S3
        redshift_s3_read_access_role = iam.Role(
            self,
            "redshiftS3AccessRole",
            role_name="redshiftS3AccessRole",
            assumed_by=iam.ServicePrincipal("redshift.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
            ],
        )

        # Crear el cluster de Redshift
        redshift_cluster = redshift.CfnCluster(
            self,
            id="redshift-cluster",
            cluster_type="single-node",
            node_type="ra3.xlplus",
            master_username="redshift-user",
            # Usar el valor del secret correctamente
            master_user_password=self.redshift_secret.secret_value_from_json("password").to_string(),
            db_name="redshift-db",
            encrypted=True,
            port=5439,
            iam_roles=[redshift_s3_read_access_role.role_arn],
            vpc_security_group_ids=[vpc.redshift_sg.security_group_id],
            cluster_subnet_group_name=subnet_group.ref,
        )
        
        # Aplicar removal policy
        redshift_cluster.apply_removal_policy(RemovalPolicy.DESTROY)
        
        # Guardar referencia al cluster
        self._instance = redshift_cluster

    @property
    def instance(self) -> redshift.CfnCluster:
        return self._instance
    
    @property
    def cluster_endpoint(self) -> str:
        """Obtener el endpoint del cluster de Redshift"""
        return self._instance.attr_endpoint_address
    
    @property
    def cluster_port(self) -> str:
        """Obtener el puerto del cluster de Redshift"""
        return self._instance.attr_endpoint_port