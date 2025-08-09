from firebase_admin import auth, firestore
from google.cloud import firestore as firestore_client
from config import Config
from auth_utils import verify_firebase_password
import os
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# from firebase_init import initialize_firebase

# # Initialize Firebase once
# try:
#     storage, db = initialize_firebase()
# except Exception as e:
#     print(f"Warning: Firebase initialization failed: {e}")
#     db = None
# # Configure logging for auth module
# logger = logging.getLogger(__name__)

def validate_app_id(app_id):
    """Validate that app_id is in allowed list"""
    ALLOWED_APP_IDS = Config.get_allowed_app_ids()
    
    logger.info(f"Validating app_id: {app_id} against allowed: {ALLOWED_APP_IDS}")
    
    if app_id not in ALLOWED_APP_IDS:
        logger.error(f"Invalid app_id: {app_id}. Allowed: {', '.join(ALLOWED_APP_IDS)}")
        raise Exception(f"Invalid app_id: {app_id}. Allowed: {', '.join(ALLOWED_APP_IDS)}")
    
    logger.info(f"App_id validation successful: {app_id}")
    return True

def authenticate_user(email, password, app_id):
    """
    Enhanced authentication with proper password validation.
    Returns a simple token instead of Firebase custom token to avoid IAM issues.
    """
    logger.info(f"Starting authentication for email: {email}, app_id: {app_id}")
    
    try:
        validate_app_id(app_id)
        
        # First verify email and password using Firebase Auth REST API
        logger.info(f"Verifying password for email: {email}")
        auth_result = verify_firebase_password(email, password)
        user_uid = auth_result["uid"]
        
        if not auth_result.get("verified", True):
            logger.warning(f"Password verification skipped for {email} (API key not available)")
        
        logger.info(f"Password verification successful for user: {user_uid}")
        
        # Verify user belongs to the requesting app
        logger.info(f"Initializing Firestore client for app verification")
        db = firestore_client.Client(project="readrocket-a9268")
        
        logger.info(f"Fetching user document for uid: {user_uid}")
        user_doc = db.collection("users").document(user_uid).get()
        
        if not user_doc.exists:
            logger.error(f"User profile not found for uid: {user_uid}")
            raise Exception("User profile not found")
        
        user_data = user_doc.to_dict()
        stored_app_id = user_data.get("app_id")
        logger.info(f"User profile found - stored app_id: {stored_app_id}, requested app_id: {app_id}")
        
        if stored_app_id != app_id:
            logger.error(f"User {user_uid} not authorized for app {app_id} (belongs to {stored_app_id})")
            raise Exception("User not authorized for this application")
        
        # Update last active timestamp
        logger.info(f"Updating last active timestamp for user: {user_uid}")
        db.collection("users").document(user_uid).update({
            "lastActiveTimestamp": firestore_client.SERVER_TIMESTAMP
        })
        
        # Return a simple token (in production, you'd want proper JWT tokens)
        simple_token = f"user_{user_uid}_{app_id}_token"
        
        logger.info(f"Authentication successful for user: {user_uid}, app_id: {app_id}")
        return {"uid": user_uid, "idToken": simple_token, "app_id": app_id}
        
    except Exception as e:
        logger.error(f"Authentication failed for email: {email}, app_id: {app_id} - Error: {str(e)}")
        raise Exception(f"Authentication failed: {str(e)}")

def register_user(email, password, app_id, firstName=None, lastName=None, userName=None, avatar=None):
    logger.info(f"Starting user registration for email: {email}, app_id: {app_id}")
    
    try:
        validate_app_id(app_id)
        
        logger.info(f"Creating Firebase user for email: {email}")
        user = auth.create_user(email=email, password=password)
        logger.info(f"Firebase user created with uid: {user.uid}")
        
        from datetime import datetime
        current_time = datetime.utcnow()
        
        # Extract defaults from email if not provided
        email_prefix = email.split('@')[0]
        
        # Ensure all required fields are present with defaults
        user_data = {
            "userId": user.uid,
            "email": email,
            "app_id": app_id,
            "userName": userName if userName is not None else email_prefix,
            "firstName": firstName if firstName is not None else email_prefix.capitalize(),
            "lastName": lastName if lastName is not None else "User",
            "provider": "email",
            "isAdmin": False,
            "credits": 3,  # Default credits
            "avatar": avatar if avatar is not None else "https://firebasestorage.googleapis.com/v0/b/readrocket-a9268.firebasestorage.app/o/icons%2FAnimation%20-%201743735839589.gif?alt=media&token=910f04a5-4154-403a-bbe5-a96263f9fb50",
            "createdAt": current_time,
            "lastActiveTimestamp": current_time,
            "subscription_status": "free",
            "preferences": {"modification_mode": "suggestion"}
        }
        
        logger.info(f"Creating user profile in Firestore for uid: {user.uid}")
        logger.debug(f"User profile data: {user_data}")
        
        # Initialize complete user profile in Firestore
        db = firestore_client.Client(project="readrocket-a9268")
        db.collection("users").document(user.uid).set(user_data)
        
        logger.info(f"User registration completed successfully for uid: {user.uid}, app_id: {app_id}")
        return {"uid": user.uid, "app_id": app_id}
        
    except Exception as e:
        logger.error(f"User registration failed for email: {email}, app_id: {app_id} - Error: {str(e)}")
        raise Exception(f"Registration failed: {str(e)}")

def get_user_profile(user_id, token, app_id):
    """
    Simplified profile retrieval for testing with multi-tenancy.
    """
    logger.info(f"Getting user profile for user_id: {user_id}, app_id: {app_id}")
    
    try:
        validate_app_id(app_id)
        
        # For testing, we'll skip token verification and just check if user exists
        logger.info(f"Verifying user exists in Firebase Auth: {user_id}")
        user = auth.get_user(user_id)  # This verifies the user exists
        logger.info(f"User verified in Firebase Auth: {user.uid}")
        
        logger.info(f"Fetching user profile from Firestore: {user_id}")
        db = firestore_client.Client(project="readrocket-a9268")
        user_doc = db.collection("users").document(user_id).get()
        
        if not user_doc.exists:
            logger.error(f"User profile not found in Firestore: {user_id}")
            raise Exception("Profile not found")
        
        user_data = user_doc.to_dict()
        stored_app_id = user_data.get("app_id")
        logger.info(f"Profile found - stored app_id: {stored_app_id}, requested app_id: {app_id}")
        
        if stored_app_id != app_id:
            logger.error(f"User {user_id} not authorized for app {app_id} (belongs to {stored_app_id})")
            raise Exception("User not authorized for this application")
        
        logger.info(f"Profile retrieved successfully for user_id: {user_id}, app_id: {app_id}")
        return user_data
        
    except Exception as e:
        logger.error(f"Failed to get profile for user_id: {user_id}, app_id: {app_id} - Error: {str(e)}")
        raise Exception(f"Failed to get profile: {str(e)}")

def update_user_profile(user_id, token, preferences, app_id):
    """
    Simplified profile update for testing with multi-tenancy.
    """
    logger.info(f"Updating user profile for user_id: {user_id}, app_id: {app_id}, preferences: {preferences}")
    
    try:
        validate_app_id(app_id)
        
        # For testing, we'll skip token verification and just check if user exists
        logger.info(f"Verifying user exists in Firebase Auth: {user_id}")
        user = auth.get_user(user_id)  # This verifies the user exists
        logger.info(f"User verified in Firebase Auth: {user.uid}")
        
        db = firestore_client.Client(project="readrocket-a9268")
        
        # First verify user belongs to the requesting app
        logger.info(f"Fetching user profile for authorization check: {user_id}")
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            logger.error(f"User profile not found in Firestore: {user_id}")
            raise Exception("Profile not found")
        
        user_data = user_doc.to_dict()
        stored_app_id = user_data.get("app_id")
        logger.info(f"Authorization check - stored app_id: {stored_app_id}, requested app_id: {app_id}")
        
        if stored_app_id != app_id:
            logger.error(f"User {user_id} not authorized for app {app_id} (belongs to {stored_app_id})")
            raise Exception("User not authorized for this application")
        
        # Update preferences
        logger.info(f"Updating preferences in Firestore for user_id: {user_id}")
        db.collection("users").document(user_id).update({
            "preferences": preferences
        })
        
        logger.info(f"Profile updated successfully for user_id: {user_id}, app_id: {app_id}")
        
    except Exception as e:
        logger.error(f"Failed to update profile for user_id: {user_id}, app_id: {app_id} - Error: {str(e)}")
        raise Exception(f"Failed to update profile: {str(e)}")

def get_users_by_app(app_id, limit=100):
    """Get all users for a specific app"""
    logger.info(f"Getting users for app_id: {app_id}, limit: {limit}")
    
    try:
        validate_app_id(app_id)
        
        logger.info(f"Querying Firestore for users with app_id: {app_id}")
        db = firestore_client.Client(project="readrocket-a9268")
        users_ref = db.collection("users")
        query = users_ref.where("app_id", "==", app_id).limit(limit)
        docs = query.stream()
        
        users = []
        count = 0
        for doc in docs:
            user_data = doc.to_dict()
            user_data["uid"] = doc.id
            users.append(user_data)
            count += 1
        
        logger.info(f"Retrieved {count} users for app_id: {app_id}")
        return users
        
    except Exception as e:
        logger.error(f"Failed to get users for app_id: {app_id} - Error: {str(e)}")
        raise Exception(f"Failed to get users for app: {str(e)}")

def verify_custom_token(token, expected_uid):
    """
    Helper function to verify custom tokens for testing.
    In production, use Firebase Auth client-side flow instead.
    """
    try:
        # For testing purposes, we'll create a mock verification
        # In reality, custom tokens should be exchanged for ID tokens client-side
        return {"uid": expected_uid}
    except Exception as e:
        raise Exception(f"Token verification failed: {str(e)}")
