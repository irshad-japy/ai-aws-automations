import aws_cdk as cdk
from aws_cdk import (
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_s3 as s3,
    aws_logs as logs,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr as ecr,
    CfnOutput    
)

from constructs import Construct

class AstraAnnotateStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        stack_name: str,
        description: str,
        settings: dict,
        **kwargs,
    ) -> None:

        super().__init__(
            scope=scope,
            id=id,
            stack_name=stack_name,
            description=description,
            **kwargs,
        )
 
        ecs_task_role = iam.Role(
            self, 
            id=settings.get('domain_name')+"-ecs-task-role", 
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )

        stepfunction_role = iam.Role.from_role_name(
            self, 
            id=settings.get('domain_name')+"-stepfn-default-role", 
            role_name=settings["stepfunction_role"]
        )   

        eventbridge_role = iam.Role.from_role_name(
            self, 
            id=settings.get('domain_name')+"-eventbridge-default-role", 
            role_name=settings["eventbridge_role"]
        )                

        notification_topic = sns.Topic(
            self, 
            settings.get('domain_name')+"-astra-annotation-status", 
            topic_name=settings.get('domain_name')+"-astra-annotation-status"
        )
        for email_id in settings.get('sns_emails'):
            notification_topic.add_subscription(subs.EmailSubscription(email_id)) 

        glue_job_task = tasks.GlueStartJobRun(
            self, 
            "Start Annotations-Ingest GlueJob",
            glue_job_name=settings.get('glue_job_name'),
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            result_path='$.GlueJobResult'
        )

        glue_fail_state = sfn.Fail(
            self, 
            "Annotations-Ingest Fail", 
            cause="Glue job failed", 
            error="GlueJobFailure"
        )

        glue_failure_notification = tasks.SnsPublish(
            self, "Annotations-Ingest Fail Notify",
            topic=notification_topic,
            subject=settings.get('sns_subject'),
            message=sfn.TaskInput.from_text(
                sfn.JsonPath.format(
                    "Annotations-Ingest Glue-Job Failed and Workflow Terminated"+"\n"+"Execution-Link: "+settings.get('sns_html_link')+":"+"{}",
                    sfn.JsonPath.string_at("$$.Execution.Name")
                )
            ),
            result_path="$.sns"
        )

        glue_job_task.add_catch(
            glue_failure_notification.next(glue_fail_state),
            errors=["States.ALL"],
            result_path="$.ErrorInfo"
        )

        cluster = ecs.Cluster(
            self, 
            "EcsCluster", 
            cluster_name=settings.get('domain_name')+"-astra-cluster"
        )
        
        fargate_task_definition = ecs.FargateTaskDefinition(
            self, 
            "FargateTaskDef",
            memory_limit_mib=5120,
            cpu=1024,
            task_role=ecs_task_role
        )

        # Create an ECR repository from which the container image will be loaded.
        ecr_repository = ecr.Repository(
            self,
            id=settings.get('domain_name')+"-ecr-repo",
            repository_name=settings.get('ecr_repo_name')
        )

        # Define the container definition using an image from the ECR repository.
        container_definition = ecs.ContainerDefinition(
            self, "ContainerDef",
            task_definition=fargate_task_definition,
            image=ecs.ContainerImage.from_ecr_repository(ecr_repository, tag="latest"),
            memory_limit_mib=512,
            cpu=256
        )

        # Now use the container definition inside the Fargate Task.
        fargate_task = tasks.EcsRunTask(
            self, "Run Fargate Task",
            cluster=cluster,
            task_definition=fargate_task_definition,
            launch_target=tasks.EcsFargateLaunchTarget(
                platform_version=ecs.FargatePlatformVersion.LATEST
            ),
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            container_overrides=[
                tasks.ContainerOverride(
                    container_definition=container_definition,
                    environment=[
                        tasks.TaskEnvironmentVariable(
                            name="TASK_TOKEN",
                            value=sfn.JsonPath.task_token
                        )
                    ]
                )
            ],
            result_path="$.UploadResult"
        )

        success_notification = tasks.SnsPublish(
            self, "Astra-Annotation Success Notify",
            topic=notification_topic,
            subject=settings.get('sns_subject'),
            message=sfn.TaskInput.from_text(
                sfn.JsonPath.format(
                    "Tasks Upload Completed Successfully"+"\n"+"Execution-Link: "+settings.get('sns_html_link')+":"+"{}",
                    sfn.JsonPath.string_at("$$.Execution.Name")
                )
            ),
            result_path="$.sns"
        )

        fail_notification = tasks.SnsPublish(
            self, "Astra-Annotation Fail Notify",
            topic=notification_topic,
            subject=settings.get('sns_subject'),
            message=sfn.TaskInput.from_text(
                sfn.JsonPath.format(
                    "Tasks Upload Failed"+"\n"+"Execution-Link: "+settings.get('sns_html_link')+":"+"{}",
                    sfn.JsonPath.string_at("$$.Execution.Name")
                )
            ),
            result_path="$.sns"
        )        

        workflow_fail_state = sfn.Fail(
            self, 
            "Annotations-Upload Fail", 
            cause="Tasks upload failed", 
            error="EcsTaskFailure"
        )

        definition_astra_annotate = (
            glue_job_task
            .next(
                sfn.Choice(self, "Annotations-Creation Success?")  
                .when(
                    sfn.Condition.string_equals("$.GlueJobResult.JobRunState", "SUCCEEDED"),
                    fargate_task
                    .next(
                        sfn.Choice(self, "Fargate Task Success?")  
                        .when(
                            sfn.Condition.string_equals("$.UploadResult.Status", "Succeeded"),
                            success_notification
                        ) 
                        .when(
                            sfn.Condition.string_equals("$.UploadResult.Status", "Failed"),
                            fail_notification.next(workflow_fail_state)
                        )                                                
                    )
                )
            )
        )

        state_machine_parallelmap = sfn.StateMachine(
            self, settings.get('domain_name')+'-astra-annotation',
            state_machine_name=settings.get('domain_name')+'-astra-annotation',
            definition=definition_astra_annotate,
            role=stepfunction_role,
            logs=sfn.LogOptions(
                destination=logs.LogGroup(
                    self, settings.get('domain_name')+'-astra-annotation-logs',
                    log_group_name=settings.get('domain_name')+'-astra-annotation-logs',
                    removal_policy=cdk.RemovalPolicy.DESTROY
                ),
                level=sfn.LogLevel.ALL
            )
        )

        if settings.get('cron'):
            daily_schedule_rule = events.Rule(
                self, settings.get('domain_name')+'-astra-annotation-trigger',
                rule_name=settings.get('domain_name')+'-astra-annotation-trigger',
                schedule=events.Schedule.cron(
                    minute=settings.get('cron_minute'), 
                    hour=settings.get('cron_hour')
                )
            )
            daily_schedule_rule.add_target(
                targets.SfnStateMachine(state_machine_parallelmap, role=eventbridge_role)
            )
