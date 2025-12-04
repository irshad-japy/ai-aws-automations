import aws_cdk as cdk
from lib.rustdesk_scheduler_stack import RustDeskSchedulerStack

app = cdk.App()
RustDeskSchedulerStack(
    app, "RustDeskSchedulerStack",
    env=cdk.Environment(account="747230718574", region="ap-south-1"),
)
app.synth()
