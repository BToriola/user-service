#!/bin/bash

# Cloud Run deployment script for the chat processing worker

set -e  # Exit immediately if a command exits with a non-zero status

# Load from .env.production into environment
export $(grep -v '^#' .env | xargs)

# Configuration
PROJECT_ID="readrocket-a9268"
SERVICE_NAME="rkt-user-service"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Optional: Check if essential environment variables are set
REQUIRED_VARS=( 
  FIREBASE_PROJECT_ID
  GOOGLE_API_KEY
  FIREBASE_STORAGE_BUCKET 
  FIREBASE_API_KEY
)

echo "Checking required environment variables..."
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var}" ]]; then
    echo "Error: Environment variable $var is not set"
    exit 1
  fi
done

# Build and push the Docker image
echo "Building and pushing Docker image..."
docker buildx build --platform linux/amd64 --load -t "$IMAGE_NAME" .
docker push "$IMAGE_NAME"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_NAME" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 900 \
  --concurrency 80 \
  --max-instances 10 \
  --port 8080 \
  --project "$PROJECT_ID" \
  --env-vars-file .env.yaml

echo "✅ Deployment complete!"
echo "🔗 Service URL: $(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')"
