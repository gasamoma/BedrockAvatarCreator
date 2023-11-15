from aws_cdk import (
    # Duration,
    Stack,
    Token,
    aws_lambda_python_alpha as python,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_cognito as _cognito,
    Duration,
    RemovalPolicy,
    CfnOutput,
    Fn,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_s3 as s3,
    aws_cloudfront as _cf,
    aws_s3_deployment as s3deploy,
    aws_cloudfront_origins as origins,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as aws_logs,
    
)
from constructs import Construct

class BedrockAvatarCreatorStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        vpc = ec2.Vpc(self, "roop-vpc",
            gateway_endpoints={
                "S3": ec2.GatewayVpcEndpointOptions(
                    service=ec2.GatewayVpcEndpointAwsService.S3)}, 
            max_azs=3)     # default is all AZs in region
        
        # add addInterfaceEndpoint for com.amazonaws.region.ecr.api
        vpc.add_interface_endpoint("ecr-api",
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            private_dns_enabled=True)
        # add addInterfaceEndpoint for com.amazonaws.region.ecr.dkr
        vpc.add_interface_endpoint("ecr-dkr",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            private_dns_enabled=True)
            
        
            
        cluster = ecs.Cluster(self, "roop-cluster", vpc=vpc)
        repository = ecr.Repository.from_repository_arn(self,"roop-repo", "arn:aws:ecr:us-east-1:016267129961:repository/roop")
        # create a task definition with FargateTaskDefinition 
        # memory_limit_mib=2048, ephemeral_storage_gib=100, cpu=1024
        task_definition = ecs.FargateTaskDefinition(self, "TaskDef",
            memory_limit_mib=4096,
            cpu=1024,
            ephemeral_storage_gib=200)
            
            
            
        task_definition.add_container("web",
            image=ecs.ContainerImage.from_ecr_repository(repository,"latest"),
            # port mappings
            port_mappings=[ecs.PortMapping(container_port=8000, host_port=8000)],
            
            # add awslogs log configuration
            logging=ecs.AwsLogDriver(
                stream_prefix="ecs",
                log_retention=aws_logs.RetentionDays.ONE_WEEK)
            )

        
        # health check to /get_execution_providers
        load_balancer = ecs_patterns.ApplicationLoadBalancedFargateService(self, "roop-service",
            cluster=cluster,            # Required
            cpu=512,                    # Default is 256
            desired_count=4,            # Default is 1
            task_definition=task_definition,
            memory_limit_mib=2048,      # Default is 512
            public_load_balancer=True
            )
        
        # set the health check path to /get_execution_providers
        
        load_balancer.target_group.configure_health_check(path="/get_execution_providers")
        load_balancer_dns = load_balancer.load_balancer.load_balancer_dns_name
        # add permisions to the fargate role to access the ecr repo to pull the image
        load_balancer.service.task_definition.add_to_execution_role_policy(iam.PolicyStatement(
            actions=["ecr:GetAuthorizationToken", "ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage"],
            resources=["*"]
            ))
        # a cognito user pool that uses cognito managed login sign up and password recovery
        user_pool = _cognito.UserPool(
            self, "Bedrock-Avatar-UserPool",
            self_sign_up_enabled=True,
            # removal policy destroy
            removal_policy=RemovalPolicy.DESTROY,
            # add email as a standard attribute
            standard_attributes=_cognito.StandardAttributes(
                email=_cognito.StandardAttribute(
                    required=True,
                    mutable=False)),
            user_verification=_cognito.UserVerificationConfig(
                email_subject="Verify your email for our awesome app!",
                email_body="Thanks for signing up to our awesome app! Your verification code is {####}",
                email_style=_cognito.VerificationEmailStyle.CODE,
                sms_message="Thanks for signing up to our awesome app! Your verification code is {####}"
            ),
            sign_in_aliases=_cognito.SignInAliases(
                email=True,
                phone=False,
                username=False))
        # create the bucket
        s3_file_bucket = s3.Bucket(
            self, "bedrock-avatar-image-store",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.KMS_MANAGED
            )
        # add cors to the put method from everywhere
        s3_file_bucket.add_cors_rule(allowed_origins=['*'],
            allowed_methods=[s3.HttpMethods.PUT],
            allowed_headers=['*'])
        
        # a lambda function called api_backend
        api_backend = python.PythonFunction(self, "ApiBackend",
            entry="app/lambda",
            index="api.py",  
            handler="lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            environment={
                #"BUCKET_NAME": s3_bucket.bucket_name,
                # post_autentication_dynamo_table_name
                "BUCKET": s3_file_bucket.bucket_name,
                "ROOP": load_balancer_dns,
                "MODELID": "stability.stable-diffusion-xl-v0"
                },
            timeout=Duration.seconds(120),
            layers=[
                python.PythonLayerVersion(self, "api_layer",
                    entry="lib/python",
                    compatible_runtimes=[_lambda.Runtime.PYTHON_3_10]
                )
            ]
        )
        
        api_back_get = python.PythonFunction(self, "ApiBackendGet",
            entry="app/lambda",
            index="api_get.py",
            handler="handler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            environment={
                    "BUCKET": s3_file_bucket.bucket_name,
                },
            timeout=Duration.seconds(120),
            layers=[
                python.PythonLayerVersion(self, "api_layer_get",
                    entry="lib/python",
                    compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
                )
            ]
        )
        get_user_files_lambda = python.PythonFunction(self, "GetUserFilesLambdaFunction",
            entry="app/lambda",
            index="get_user_files.py",
            handler="lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            environment={
                "BUCKET_NAME": s3_file_bucket.bucket_name
            },
            timeout=Duration.seconds(120),
            layers=[
                python.PythonLayerVersion(self, "GetUserFilesLambdaFunction_layer",
                    entry="lib/python",
                    compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
                )
            ]
        )
        
        get_user_files_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:GetObjectVersion"
                    ],
                resources=[s3_file_bucket.bucket_arn,s3_file_bucket.bucket_arn + "/*"]))
        # add permisions to api_back_get to presing urls from s3 to put
        s3_file_bucket.grant_put(api_back_get,objects_key_pattern="input/*")
        # add permisions to api_back_get to presing urls from s3 to write
        s3_file_bucket.grant_write(api_back_get,objects_key_pattern="input/*")
        s3_file_bucket.grant_read(api_back_get,objects_key_pattern="input/*")
        # add permisions to api_backend AmazonS3ReadOnlyAccess
        s3_file_bucket.grant_read(api_backend)
        # add alpermisions to api_backend to lsi s3_file_bucket
        api_backend.add_to_role_policy(iam.PolicyStatement(
            actions=["s3:ListBucket", "s3:GetObject","s3:PutObject","s3:PutObjectAcl","s3:GetObjectAcl"],
            resources=[
                s3_file_bucket.bucket_arn,
                s3_file_bucket.bucket_arn + "/*"]
            ))
        # add permisions to api_backend to rekognition full access
        api_backend.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:*"],
            resources=["*"]
            ))
            # add permisions to api_backend to rekognition full access
        api_backend.add_to_role_policy(iam.PolicyStatement(
            actions=["rekognition:*"],
            resources=["*"]
            ))
        
        # add permisions to rekognition service to read from s3_file_bucket

        
        # an API gateway that with cors for the cloudfront
        api_gateway = apigateway.RestApi(
            self, "ApiGWBackend",
            rest_api_name="Bedrock-AvatarApiGateway",
            description="This is the bedrockAvatar API Gateway",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=["*"],
                # TODO allow the cloufront distribution
                allow_origins=["*"],
                allow_headers=["*"])
                )
        
        domain = user_pool.add_domain("CognitoDomain",
            cognito_domain=_cognito.CognitoDomainOptions(
                domain_prefix="bedrock-avatar-creator-domain-000001"
            )
        )
        
        s3_website_bucket = s3.Bucket(
            self, "bedrock-Avatar-WebsiteBucket"
            )
        s3deploy.BucketDeployment(self, "DeployWebsite",
            sources=[s3deploy.Source.asset("./web/")],
            destination_bucket=s3_website_bucket
        )
        
        # create an origin access identity
        oin = _cf.OriginAccessIdentity(
            self, "bedrock-AvatarOriginAccessIdentity",
            comment="bedrock-AvatarOriginAccessIdentity")
        # give permisions to the origin_access_identity to access the s3_website_bucket
        s3_website_bucket.grant_read(oin)
        # a cloudfront distribution for the s3_website_bucket
        cloudfront_website = _cf.Distribution(
            self,
            "bedrock-AvatarWebsiteDistribution",
            default_behavior=_cf.BehaviorOptions(
                allowed_methods=_cf.AllowedMethods.ALLOW_ALL,
                origin=origins.S3Origin(
                    s3_website_bucket,
                    origin_access_identity=oin)))
        
        redirect_uri="https://"+cloudfront_website.distribution_domain_name+"/index.html"
        
        # a cognito client with callback to the cloudfront_website
        client = user_pool.add_client("app-client",
            o_auth=_cognito.OAuthSettings(
                flows=_cognito.OAuthFlows(
                    implicit_code_grant=True
                ),
                # the cloudfront distribution root url
                callback_urls=[redirect_uri]
            ),
            auth_flows=_cognito.AuthFlow(
                user_password=True,
                user_srp=True
            )
        )
        sign_in_url = domain.sign_in_url(client,
            redirect_uri=redirect_uri
        )
        
        # a method for the api that calls the bedrock lambda function
        api_backend_integration = apigateway.LambdaIntegration(api_backend,
                request_templates={"application/json": '{ "statusCode": "200" }'})
       
        api_backend_get_integration = apigateway.LambdaIntegration( api_back_get,
                request_templates={"application/json": '{ "statusCode": "200" }'})
                
        get_user_files_integration = apigateway.LambdaIntegration(get_user_files_lambda,
                request_templates={"application/json": '{ "statusCode": "200" }'})
                
        # add the  LambdaIntegration to the api gateway using user_pool as the authorization
        api_backend_resource = api_gateway.root.add_resource("api_backend")
        get_user_files_resource = api_gateway.root.add_resource("get_user_files")
        
        autorizer=apigateway.CognitoUserPoolsAuthorizer(
                self, "IdpAuthorizer",
                cognito_user_pools=[user_pool])
        method_api_backend = api_backend_resource.add_method(
            "POST", api_backend_integration,
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=autorizer)
        method_get_user_files = get_user_files_resource.add_method(
            "POST", get_user_files_integration,
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=autorizer)
        method_api_backend_get = api_backend_resource.add_method(
            "GET", api_backend_get_integration,
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=autorizer)

        deployment = apigateway.Deployment(self, "Deployment",
            api=api_gateway,
            description="This is the bedrockAvatar API Gateway Deployment")
            
        s3_file_bucket.add_cors_rule(allowed_origins=["*"],# TODO Only allow cloudfront_website
            allowed_methods=[s3.HttpMethods.PUT],
            allowed_headers=['*'])
            
        ssm.StringParameter(self, "user_pool_login_url",
            parameter_name="user_pool_login_url"+construct_id,
            string_value=sign_in_url)
        # CfnOutput the user_pool login url
        CfnOutput(self, "UserPoolLoginUrl", value=sign_in_url)
        CfnOutput(self, "LoadbalancerDNS", value=load_balancer_dns)
