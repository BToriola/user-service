from firebase_admin import auth, firestore
from google.cloud import firestore as firestore_client
from config import Config
from firebase_init import initialize_firebase
import os
# load env variables


# Initialize Firebase once
try:
    storage, db = initialize_firebase()
except Exception as e:
    print(f"Warning: Firebase initialization failed: {e}")
    db = None

def authenticate_user(email, password, app_id):
    """
    Simplified authentication that doesn't require custom token creation.
    Returns a simple token for testing purposes.
    """
    if db is None:
        raise Exception("Firebase not initialized. Please check service account configuration.")
    
    try:
        user = auth.get_user_by_email(email)
        
        # Verify user belongs to the requesting app
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

def register_user(email, password, app_id):
    if db is None:
        raise Exception("Firebase not initialized. Please check service account configuration.")
    
    try:
        user = auth.create_user(email=email, password=password)
        # Initialize user profile in Firestore with app_id for multi-tenancy
        db.collection("users").document(user.uid).set({
            "email": email,
            "app_id": app_id,
            "subscription_status": "free",
            "preferences": {"modification_mode": "suggestion"},
            "created_at": firestore.SERVER_TIMESTAMP
        })
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
        
        # First verify user belongs to the requesting app
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise Exception("Profile not found")
        
        user_data = user_doc.to_dict()
        if user_data.get("app_id") != app_id:
            raise Exception("User not authorized for this application")
        
        # Update preferences
        db.collection("users").document(user_id).update({
            "preferences": preferences,
            "updated_at": firestore_client.SERVER_TIMESTAMP
        })
    except Exception as e:
        raise Exception(f"Failed to update profile: {str(e)}")

def get_users_by_app(app_id, limit=100):
    """Get all users for a specific app"""
    try:
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

def validate_app_id(app_id):
    """Validate that app_id is in allowed list"""
    ALLOWED_APP_IDS = Config.get_allowed_app_ids()
    
    if app_id not in ALLOWED_APP_IDS:
        raise Exception(f"Invalid app_id: {app_id}. Allowed: {', '.join(ALLOWED_APP_IDS)}")
    
    return True