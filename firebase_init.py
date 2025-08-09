# firebase_init.py
from firebase_admin import credentials, initialize_app, storage, firestore
import logging
import os
from pathlib import Path

def initialize_firebase():
    """Initialize Firebase with credentials if not already initialized"""
    try:
        # Try to get an existing app
        storage.bucket()
        return storage, firestore.client()
    except ValueError:
        # Initialize new app if none exists
        service_account_path = "rrkt-firebase-adminsdk.json"
        
        if os.path.exists(service_account_path):
            # Use local service account file
            cred = credentials.Certificate(service_account_path)
        elif os.getenv('FIREBASE_CREDENTIALS_PATH'):
            # Use path from environment variable
            cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
        elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
            # For services like Heroku where we pass JSON as env var
            import json
            cred_dict = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
            cred = credentials.Certificate(cred_dict)
        else:
            # Use default credentials as fallback (for Cloud Run with default service account)
            cred = credentials.ApplicationDefault()
        
        # Initialize Firebase app
        initialize_app(cred, {
            'storageBucket': 'readrocket-a9268.firebasestorage.app'
        })
        
        logging.info("Firebase initialized successfully")
        return storage, firestore.client()
    except Exception as e:
        logging.error(f"Failed to initialize Firebase: {e}")
        raise
