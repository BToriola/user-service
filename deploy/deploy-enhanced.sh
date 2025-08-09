#!/bin/bash

# Enhanced Cloud Run deployment script with proper Firebase permissions

set -e  # Exit immediately if a command exits with a non-zero status

# Configuration
PROJECT_ID="readrocket-a9268"
SERVICE_NAME="rkt-user-service"
REGION="us-central1"
SERVICE_ACCOUNT="firebase-adminsdk-gsfo9@readrocket-a9268.iam.gserviceaccount.com"

echo "🚀 Starting enhanced deployment to Cloud Run..."

# Check if service account key exists
if [ ! -f "rrkt-firebase-adminsdk.json" ]; then
    echo "❌ Error: rrkt-firebase-adminsdk.json not found!"
    echo "Please place your Firebase service account key in the project root."
    exit 1
fi

echo "✅ Service account key found"

# Authenticate with Google Cloud if needed
echo "Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "Please authenticate with Google Cloud:"
    gcloud auth login
fi

# Set project
gcloud config set project "$PROJECT_ID"

# Fix quota project issue
echo "Setting quota project to match active project..."
gcloud auth application-default set-quota-project "$PROJECT_ID"

# Grant necessary permissions to the service account
echo "🔐 Ensuring service account has proper permissions..."

# Firebase Admin permissions
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/firebase.admin" || echo "Firebase admin role already granted or not available"

# Firestore permissions
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/datastore.user" || echo "Datastore role already granted"

# Firebase Auth permissions
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/firebase.developAdmin" || echo "Firebase develop admin role already granted or not available"

# Token creator permission for custom tokens
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/iam.serviceAccountTokenCreator" || echo "Token creator role already granted"

# Build and deploy to Cloud Run
echo "📦 Building and deploying to Cloud Run..."
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
  --service-account "$SERVICE_ACCOUNT" \
  --set-env-vars "ALLOWED_APP_IDS=readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-env-vars "FIREBASE_API_KEY=AIzaSyACt2SPVeRwAKGW6wu2Jt80Q806mbgq0ig" \
  --set-env-vars "GOOGLE_APPLICATION_CREDENTIALS=/app/rrkt-firebase-adminsdk.json" \
  --set-env-vars "FIREBASE_CREDENTIALS_PATH=/app/rrkt-firebase-adminsdk.json"

echo "✅ Deployment complete!"

# Get and display service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')
echo "🔗 Service URL: $SERVICE_URL"

# Test the deployment
echo "🧪 Testing deployment..."
if curl -s "$SERVICE_URL/health" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

echo "🎉 Enhanced deployment completed successfully!"
