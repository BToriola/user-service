from firebase_admin import auth, firestore
from google.cloud import firestore as firestore_client
from config import Config
import os

def validate_app_id(app_id):
    """Validate that app_id is in allowed list"""
    ALLOWED_APP_IDS = Config.get_allowed_app_ids()
    
    if app_id not in ALLOWED_APP_IDS:
        raise Exception(f"Invalid app_id: {app_id}. Allowed: {', '.join(ALLOWED_APP_IDS)}")
    
    return True

def authenticate_user(email, password, app_id):
    """
    Simplified authentication for testing purposes with multi-tenancy.
    Returns a simple token instead of Firebase custom token to avoid IAM issues.
    """
    try:
        validate_app_id(app_id)
        user = auth.get_user_by_email(email)
        
        # Verify user belongs to the requesting app
        db = firestore_client.Client(project="readrocket-a9268")
        user_doc = db.collection("users").document(user.uid).get()
        
        if not user_doc.exists:
            raise Exception("User profile not found")
        
        user_data = user_doc.to_dict()
        if user_data.get("app_id") != app_id:
            raise Exception("User not authorized for this application")
        
        # Update last active timestamp
        db.collection("users").document(user.uid).update({
            "lastActiveTimestamp": firestore_client.SERVER_TIMESTAMP
        })
        
        # Return a simple token (in production, you'd want proper JWT tokens)
        simple_token = f"user_{user.uid}_{app_id}_token"
        return {"uid": user.uid, "idToken": simple_token, "app_id": app_id}
    except auth.UserNotFoundError:
        raise Exception("User not found")
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")

def register_user(email, password, app_id, firstName=None, lastName=None, userName=None, avatar=None):
    try:
        validate_app_id(app_id)
        user = auth.create_user(email=email, password=password)
        
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
        
        # Initialize complete user profile in Firestore
        db = firestore_client.Client(project="readrocket-a9268")
        db.collection("users").document(user.uid).set(user_data)
        
        return {"uid": user.uid, "app_id": app_id}
    except Exception as e:
        raise Exception(f"Registration failed: {str(e)}")

def get_user_profile(user_id, token, app_id):
    """
    Simplified profile retrieval for testing with multi-tenancy.
    """
    try:
        validate_app_id(app_id)
        # For testing, we'll skip token verification and just check if user exists
        user = auth.get_user(user_id)  # This verifies the user exists
        
        db = firestore_client.Client(project="readrocket-a9268")
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise Exception("Profile not found")
        
        user_data = user_doc.to_dict()
        if user_data.get("app_id") != app_id:
            raise Exception("User not authorized for this application")
        
        return user_data
    except Exception as e:
        raise Exception(f"Failed to get profile: {str(e)}")

def update_user_profile(user_id, token, preferences, app_id):
    """
    Simplified profile update for testing with multi-tenancy.
    """
    try:
        validate_app_id(app_id)
        # For testing, we'll skip token verification and just check if user exists
        user = auth.get_user(user_id)  # This verifies the user exists
        
        db = firestore_client.Client(project="readrocket-a9268")
        
        # First verify user belongs to the requesting app
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise Exception("Profile not found")
        
        user_data = user_doc.to_dict()
        if user_data.get("app_id") != app_id:
            raise Exception("User not authorized for this application")
        
        # Update preferences
        db.collection("users").document(user_id).update({
            "preferences": preferences
        })
    except Exception as e:
        raise Exception(f"Failed to update profile: {str(e)}")

def get_users_by_app(app_id, limit=100):
    """Get all users for a specific app"""
    try:
        validate_app_id(app_id)
        db = firestore_client.Client(project="readrocket-a9268")
        users_ref = db.collection("users")
        query = users_ref.where("app_id", "==", app_id).limit(limit)
        docs = query.stream()
        
        users = []
        for doc in docs:
            user_data = doc.to_dict()
            user_data["uid"] = doc.id
            users.append(user_data)
        
        return users
    except Exception as e:
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
