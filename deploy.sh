#!/bin/bash

# Cloud Run deployment script for user service

set -e  # Exit immediately if a command exits with a non-zero status

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
else
    echo "Warning: .env file not found"
fi

# Configuration
PROJECT_ID="readrocket-a9268"
SERVICE_NAME="rkt-user-service"
REGION="us-central1"

# Authenticate with Google Cloud if needed
echo "Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "Please authenticate with Google Cloud:"
    gcloud auth login
fi

# Set project
gcloud config set project "$PROJECT_ID"

# Deploy to Cloud Run from source
echo "Deploying to Cloud Run from source..."
gcloud run deploy "$SERVICE_NAME" \
  --source . \
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
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

echo "✅ Deployment complete!"
echo "🔗 Service URL: $(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')"
