import os
import logging

# Configure logging for config module
logger = logging.getLogger(__name__)

class Config:
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "/path/to/firebase-credentials.json")
    PORT = os.getenv("PORT", "8080")
    
    # Allowed app IDs - can be overridden by environment variable
    ALLOWED_APP_IDS = os.getenv(
        "ALLOWED_APP_IDS", 
        "readrocket-web,readrocket-mobile,readrocket-admin,aijobpro-web"
    ).split(",")
    
    @classmethod
    def get_allowed_app_ids(cls):
        """Get list of allowed app IDs, stripped of whitespace"""
        app_ids = [app_id.strip() for app_id in cls.ALLOWED_APP_IDS if app_id.strip()]
        logger.info(f"Loaded allowed app IDs: {app_ids}")
        return app_ids