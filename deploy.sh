#!/bin/bash

# Cloud Run deployment script for user service

set -e  # Exit immediately if a command exits with a non-zero status


# Load from .env.production into environment
export $(grep -v '^#' .env | xargs)
# Configuration
PROJECT_ID="readrocket-a9268"
SERVICE_NAME="rkt-user-service"
REGION="us-central1"




# Optional: Check if essential environment variables are set
REQUIRED_VARS=( 
  FIREBASE_PROJECT_ID
  GOOGLE_API_KEY
  FIREBASE_STORAGE_BUCKET 
)

echo "Checking required environment variables..."
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var}" ]]; then
    echo "Error: Environment variable $var is not set"
    exit 1
  fi
done
echo "🚀 Starting deployment to Cloud Run..."

# Check if service account key exists
if [ ! -f "rrkt-firebase-adminsdk.json" ]; then
    echo "❌ Error: rrkt-firebase-adminsdk.json not found!"
    echo "Please place your Firebase service account key in the project root."
    exit 1
fi

echo "✅ Service account key found"

# Check if environment config exists
if [ ! -f ".env.yaml" ]; then
    echo "❌ Error: .env.yaml not found!"
    echo "Creating default .env.yaml file..."
    cat > .env.yaml << EOF 
EOF
    echo "✅ Created .env.yaml file"
else
    echo "✅ Environment config found"
fi

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
else
    echo "Warning: .env file not found"
fi

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

# Deploy to Cloud Run from source
echo "📦 Deploying to Cloud Run from source..."
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
  --env-vars-file .env.yaml \
  --service-account "firebase-adminsdk-gsfo9@readrocket-a9268.iam.gserviceaccount.com"

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

echo "🎉 Deployment completed successfully!"
