# RustDesk EC2 Scheduler — CDK (Python)

This CDK stack:
- Starts your EC2 at **09:00 IST** (03:30 UTC).
- Stops it at **21:00 IST** (15:30 UTC) every day.
- Adds an **extra Friday stop at 09:00 IST**.
- Stops early when **idle for 30 minutes** (CPU ≤ 3% AND Network ≤ 5 MB).

# Bootstrap (first time per account/region)
cdk bootstrap aws://747230718574/ap-south-1

# 2) Set AWS profile & region (and verify)
$env:AWS_PROFILE = "personal"
$env:CDK_DEFAULT_REGION = "ap-south-1"
aws sts get-caller-identity --profile $env:AWS_PROFILE
$env:CDK_DEFAULT_ACCOUNT = (aws sts get-caller-identity --query Account --output text --profile $env:AWS_PROFILE)

# 2)Just pass -c instanceId=... whenever you synth/deploy
cdk synth -c instanceId=i-09c40c2e332da8c67 --profile $env:AWS_PROFILE

# 3) (optional) re-bootstrap if you changed account/region — otherwise skip
cdk bootstrap aws://747230718574/ap-south-1

# 4) Deploy the new version
cdk deploy RustDeskSchedulerStack --require-approval never

--------------------------------------------------------
if you want to destroy cdk use below command
# 2) Destroy the old stack (no prompts)
cdk destroy RustDeskSchedulerStack --force

# 1) (optional) confirm the stack name
cdk ls   # should show: RustDeskSchedulerStack
