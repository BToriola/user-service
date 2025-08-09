#!/bin/bash

# Simple deployment script for Cloud Run with service account key

set -e

echo "🚀 Starting deployment to Cloud Run..."

# Configuration
PROJECT_ID="readrocket-a9268"
SERVICE_NAME="rkt-user-service"
REGION="us-central1"

# Check if service account key exists
if [ ! -f "rrkt-firebase-adminsdk.json" ]; then
    echo "❌ Error: rrkt-firebase-adminsdk.json not found!"
    echo "Please place your Firebase service account key in the project root."
    exit 1
fi

echo "✅ Service account key found"

# Set project
gcloud config set project "$PROJECT_ID"

# Deploy to Cloud Run from source
echo "📦 Deploying to Cloud Run..."
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
  --set-env-vars "ALLOWED_APP_IDS=readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web"

echo "✅ Deployment complete!"
echo "🔗 Service URL: $(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')"

# Test the deployment
echo "🧪 Testing deployment..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')
curl -s "$SERVICE_URL/health" | grep -q "healthy" && echo "✅ Health check passed" || echo "❌ Health check failed"

echo "🎉 Deployment completed successfully!"
