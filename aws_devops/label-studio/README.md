## For docker image build and push images to ECR follow below steps

 aws ecr get-login-password --region us-east-1
Step 1: Authenticate Docker to AWS ECR
aws ecr --region us-east-1 | docker login -u AWS --password-stdin <your-pass-key>

if reauthenticate asked:
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 1234567890.dkr.ecr.us-east-1.amazonaws.com

Step 2: Create an ECR Repository (if not created)
aws ecr create-repository --repository-name aia-dev-irshad-label-studio-ecr-repo

Step 3: Build the Docker Image
docker build -t aia-dev-irshad-label-studio-ecr-repo .

Step 4: Tag the Image for ECR
docker tag aia-dev-irshad-label-studio-ecr-repo:latest 1234567890.dkr.ecr.us-east-1.amazonaws.com/aia-dev-irshad-label-studio-ecr-repo:latest

Step 5: Push the Image to AWS ECR
docker push 1234567890.dkr.ecr.us-east-1.amazonaws.com/aia-dev-irshad-label-studio-ecr-repo:latest