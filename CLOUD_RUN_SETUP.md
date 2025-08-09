# Cloud Run Deployment Guide

## Prerequisites

1. **Google Cloud CLI** installed and authenticated
2. **Firebase service account key** (`rrkt-firebase-adminsdk.json`)
3. **Project permissions** in readrocket-a9268

## Setup Instructions

### 1. Service Account Key Setup

**Option A: Include in Docker Image (Recommended for simplicity)**

1. Place your service account key in the project root:
   ```bash
   # Copy your Firebase service account key to the project root
   cp path/to/your/firebase-service-account.json rrkt-firebase-adminsdk.json
   ```

2. The Dockerfile will automatically include it in the image
3. **Security Note**: Add `rrkt-firebase-adminsdk.json` to `.gitignore` to avoid committing to version control

**Option B: Cloud Secret Manager (Recommended for production)**

1. Store the service account key in Secret Manager:
   ```bash
   gcloud secrets create firebase-service-account-key --data-file=rrkt-firebase-adminsdk.json
   ```

2. Update the Cloud Run service to access the secret:
   ```bash
   gcloud run services update rkt-user-service \
     --update-secrets="/app/rrkt-firebase-adminsdk.json=firebase-service-account-key:latest" \
     --region=us-central1
   ```

**Option C: Environment Variable (Alternative)**

1. Convert service account to base64:
   ```bash
   base64 -i rrkt-firebase-adminsdk.json
   ```

2. Set as environment variable in Cloud Run:
   ```bash
   gcloud run services update rkt-user-service \
     --set-env-vars="GOOGLE_APPLICATION_CREDENTIALS_JSON=<base64_content>" \
     --region=us-central1
   ```

### 2. Deploy to Cloud Run

**Quick Deploy (with service account file):**
```bash
# Ensure service account key is in place
ls rrkt-firebase-adminsdk.json

# Deploy
./deploy.sh
```

**Manual Deploy:**
```bash
# Set project
gcloud config set project readrocket-a9268

# Deploy from source
gcloud run deploy rkt-user-service \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 900 \
  --concurrency 80 \
  --max-instances 10 \
  --port 8080 \
  --set-env-vars "ALLOWED_APP_IDS=readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web"
```

### 3. Environment Variables

Set required environment variables:

```bash
gcloud run services update rkt-user-service \
  --set-env-vars="ALLOWED_APP_IDS=readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web" \
  --region=us-central1
```

Or create `.env.yaml` file:
```yaml
# .env.yaml
ALLOWED_APP_IDS: "readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web"
PORT: "8080"
```

Deploy with env file:
```bash
gcloud run deploy rkt-user-service \
  --source . \
  --env-vars-file .env.yaml \
  --region us-central1
```

### 4. Verify Deployment

Test the health endpoint:
```bash
curl https://rkt-user-service-685994944265.us-central1.run.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "userservice"
}
```

## Security Best Practices

### 1. Service Account Permissions

Ensure your Firebase service account has minimal required permissions:
- Firebase Admin SDK Admin Service Agent
- Cloud Datastore User (for Firestore)

### 2. .gitignore

Add to `.gitignore`:
```
# Firebase credentials
rrkt-firebase-adminsdk.json
*.json

# Environment files
.env
.env.local
.env.production

# Cloud deployment
.gcloudignore
```

### 3. IAM and Access

For production, consider:
- Using Cloud Run with authentication required
- Implementing API keys or proper OAuth
- Setting up VPC connector for internal services

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   ```bash
   # Check service account permissions
   gcloud projects get-iam-policy readrocket-a9268
   ```

2. **Firebase Init Errors**
   ```bash
   # Check if service account file exists in container
   gcloud run services logs read rkt-user-service --region=us-central1
   ```

3. **Environment Variable Issues**
   ```bash
   # Check current environment variables
   gcloud run services describe rkt-user-service --region=us-central1 --format="value(spec.template.spec.template.spec.containers[0].env[].name,spec.template.spec.template.spec.containers[0].env[].value)"
   ```

### Debug Mode

Enable debug logging:
```bash
gcloud run services update rkt-user-service \
  --set-env-vars="LOG_LEVEL=DEBUG" \
  --region=us-central1
```

## File Structure

```
user-service/
├── app.py                    # Main Flask application
├── firebase_init.py          # Firebase initialization
├── auth_simple.py           # Authentication logic
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── dockerfile              # Docker configuration
├── deploy.sh               # Deployment script
├── rrkt-firebase-adminsdk.json  # Service account key (not in git)
└── .env.yaml               # Environment variables for Cloud Run
```

## Next Steps

1. Set up monitoring and logging
2. Implement proper authentication tokens
3. Add rate limiting
4. Set up CI/CD pipeline
5. Configure custom domain
