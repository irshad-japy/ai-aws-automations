#!/bin/bash

# Set these
AWS_ACCOUNT_ID="927721130786"
REGION="ap-southeast-2"
REPO_NAME="tge-glue-image"

# Tag name
IMAGE_TAG="latest"
FULL_IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"

echo "🔧 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

echo "🐳 Building image..."
docker build -t $REPO_NAME .

echo "🏷️ Tagging image..."
docker tag $REPO_NAME:latest $FULL_IMAGE_URI

echo "📤 Pushing to ECR..."
docker push $FULL_IMAGE_URI

echo "✅ Done! Image pushed to $FULL_IMAGE_URI"
