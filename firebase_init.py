# firebase_init.py
from firebase_admin import credentials, initialize_app, storage, firestore
import logging
import os
from pathlib import Path

# Configure logging for Firebase module
logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase with credentials if not already initialized"""
    logger.info("Starting Firebase initialization")
    
    try:
        # Try to get an existing app
        logger.info("Checking for existing Firebase app")
        storage.bucket()
        logger.info("Firebase app already initialized - reusing existing connection")
        return storage, firestore.client()
        
    except ValueError:
        logger.info("No existing Firebase app found - initializing new app")
        
        # Initialize new app if none exists
        # Get absolute path to service account file for local development
        current_dir = os.path.dirname(os.path.abspath(__file__))
        service_account_path = os.path.join(current_dir, "rrkt-firebase-adminsdk.json")
        
        logger.info(f"Checking environment: GOOGLE_CLOUD_PROJECT={os.getenv('GOOGLE_CLOUD_PROJECT')}")
        
        # Determine credential source based on environment
        if os.getenv('GOOGLE_CLOUD_PROJECT'):
            # Running in Google Cloud - use service account from Secret Manager
            logger.info("Running in Google Cloud - retrieving service account from Secret Manager")
            try:
                from google.cloud import secretmanager
                client = secretmanager.SecretManagerServiceClient()
                project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
                secret_name = f"projects/{project_id}/secrets/rrkt-firebase-adminsdk/versions/latest"
                response = client.access_secret_version(request={"name": secret_name})
                secret_payload = response.payload.data.decode("UTF-8")
                
                import json
                cred_dict = json.loads(secret_payload)
                cred = credentials.Certificate(cred_dict)
                logger.info("Successfully loaded service account from Secret Manager")
            except Exception as secret_error:
                logger.warning(f"Failed to load from Secret Manager: {secret_error}")
                logger.info("Falling back to default application credentials")
                cred = credentials.ApplicationDefault()
        elif os.path.exists(service_account_path):
            # Local development - use service account file
            logger.info(f"Local development - using service account file: {service_account_path}")
            cred = credentials.Certificate(service_account_path)
        elif os.getenv('FIREBASE_CREDENTIALS_PATH'):
            # Use path from environment variable
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            logger.info(f"Using service account from environment path: {cred_path}")
            cred = credentials.Certificate(cred_path)
        elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
            # For services like Heroku where we pass JSON as env var
            logger.info("Using service account from environment JSON")
            import json
            cred_dict = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
            cred = credentials.Certificate(cred_dict)
        else:
            # Fallback to default credentials
            logger.info("Using default application credentials as fallback")
            cred = credentials.ApplicationDefault()
        
        # Initialize Firebase app
        logger.info("Initializing Firebase app with storage bucket: readrocket-a9268.firebasestorage.app")
        initialize_app(cred, {
            'storageBucket': 'readrocket-a9268.firebasestorage.app'
        })
        
        logger.info("Firebase initialized successfully")
        return storage, firestore.client()
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}", exc_info=True)
        raise