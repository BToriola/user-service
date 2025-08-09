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
        # Get absolute path to service account file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        service_account_path = os.path.join(current_dir, "rrkt-firebase-adminsdk.json")
        
        logger.info(f"Looking for service account file at: {service_account_path}")
        
        if os.path.exists(service_account_path):
            logger.info(f"Using local service account file: {service_account_path}")
            cred = credentials.Certificate(service_account_path)
        elif os.getenv('FIREBASE_CREDENTIALS_PATH'):
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            logger.info(f"Using service account from environment path: {cred_path}")
            cred = credentials.Certificate(cred_path)
        elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
            logger.info("Using service account from environment JSON")
            # For services like Heroku where we pass JSON as env var
            import json
            cred_dict = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
            cred = credentials.Certificate(cred_dict)
        else:
            logger.info("Using default application credentials (for Cloud Run)")
            # Use default credentials as fallback (for Cloud Run with default service account)
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
