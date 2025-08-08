# User Service Configuration Guide

## Environment Variables

The User Service supports configuration via environment variables to make it flexible for different deployment environments.

### Required Environment Variables

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=readrocket-a9268
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_STORAGE_BUCKET=readrocket-a9268.firebasestorage.app

# Google Cloud
GOOGLE_API_KEY=your_google_api_key
```

### Optional Environment Variables

```bash
# Service Configuration
PORT=8080                    # Default: 8080

# Multi-tenant App Configuration
ALLOWED_APP_IDS=readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web

# Firebase Authentication (choose one)
FIREBASE_CREDENTIALS_PATH=/path/to/service-account.json
# OR
GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type":"service_account",...}'
```

## Multi-Tenancy Configuration

### App IDs

The service supports multiple applications through the `ALLOWED_APP_IDS` environment variable. This controls which applications can access the service.

**Default App IDs:**
- `readrocket-web` - Web application
- `readrocket-mobile` - Mobile application  
- `readrocket-admin` - Admin dashboard
- `aijobpro-web` - AI Job Pro web application

### Adding New App IDs

To add new applications:

1. **Development/Local:**
   ```bash
   export ALLOWED_APP_IDS="readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web,new-app-id"
   ```

2. **Production (Cloud Run):**
   Update your `.env.yaml` file:
   ```yaml
   ALLOWED_APP_IDS: "readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web,new-app-id"
   ```

3. **Docker:**
   ```bash
   docker run -e ALLOWED_APP_IDS="readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web,new-app-id" your-image
   ```

### App ID Format

- Use lowercase letters, numbers, and hyphens
- No spaces or special characters
- Be descriptive: `company-app-platform` format recommended

## Deployment Configuration

### Cloud Run

Create `.env.yaml` file:
```yaml
# Required
FIREBASE_PROJECT_ID: "readrocket-a9268"
FIREBASE_API_KEY: "your_api_key"
FIREBASE_STORAGE_BUCKET: "readrocket-a9268.firebasestorage.app"
GOOGLE_API_KEY: "your_google_api_key"

# Optional
PORT: "8080"
ALLOWED_APP_IDS: "readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web"
```

Deploy with:
```bash
gcloud run deploy your-service --env-vars-file .env.yaml
```

### Local Development

Create `.env` file:
```bash
# Copy from .env.example and customize
cp .env.example .env
```

Edit `.env` with your values:
```bash
FIREBASE_PROJECT_ID=readrocket-a9268
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-credentials.json
ALLOWED_APP_IDS=readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web
```

## Security Notes

1. **App ID Validation**: Only whitelisted app IDs can access the service
2. **Environment Variables**: Never commit sensitive values to version control
3. **Service Account**: Use appropriate Firebase service account permissions
4. **Network Security**: Configure firewall rules for production deployments

## Configuration Validation

The service validates configuration on startup:

- **App IDs**: Must be non-empty strings, comma-separated
- **Firebase**: Project ID and credentials must be valid
- **Port**: Must be a valid port number

Invalid configurations will cause the service to fail to start with descriptive error messages.

## Troubleshooting

### Common Issues

1. **Invalid app_id error**: Check `ALLOWED_APP_IDS` environment variable
2. **Firebase auth errors**: Verify `FIREBASE_PROJECT_ID` and credentials
3. **Service won't start**: Check all required environment variables are set

### Debug Configuration

Add to your environment for debugging:
```bash
LOG_LEVEL=DEBUG
```

This will show configuration loading and validation details in the logs.
