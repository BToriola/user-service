# firebase_init.py
from firebase_admin import credentials, initialize_app, storage, firestore
import logging
import os
from pathlib import Path

#load env variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging for Firebase module
logger = logging.getLogger(__name__)
# Firebase setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRED_PATH = os.path.join(BASE_DIR, './rrkt-firebase-adminsdk.json')
PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_PROJECT_ID = PROJECT_ID
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")  

def initialize_firebase():
    """Initialize Firebase with credentials if not already initialized"""
    try:
        # Try to get an existing app
        storage.bucket()
        return storage, firestore.client()
    except ValueError:
        # Initialize new app if none exists
        cred = credentials.Certificate("rrkt-firebase-adminsdk.json")
        initialize_app(cred, {
            'projectId': PROJECT_ID ,
            'storageBucket': 'readrocket-a9268.firebasestorage.app'
        })
        return storage, firestore.client()
    
# # Initialize Firebase
# try:
#     cred = credentials.Certificate(CRED_PATH)
#     initialize_app(cred, {
#         'storageBucket': FIREBASE_STORAGE_BUCKET,
#         'projectId': PROJECT_ID 
#     })
#     storage_client = storage.Client()
#     firestore_client = firestore.Client()
# except Exception as e:
#     logger.error(f"Firebase initialization error: {e}")