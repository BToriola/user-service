from firebase_admin import auth, firestore
from google.cloud import firestore as firestore_client
from config import Config
import os

def authenticate_user(email, password, app_id):
    # Firebase Authentication doesn't directly support password verification in Admin SDK.
    # Instead, we simulate login by creating a custom token and exchanging it client-side.
    # For simplicity, assume client sends ID token after Firebase Auth login.
    # Here, we verify the email exists and belongs to the correct app.
    try:
        user = auth.get_user_by_email(email)
        
        # Verify user belongs to the requesting app
        db = firestore_client.Client(project="readrocket-a9268")
        user_doc = db.collection("users").document(user.uid).get()
        
        if not user_doc.exists:
            raise Exception("User profile not found")
        
        user_data = user_doc.to_dict()
        if user_data.get("app_id") != app_id:
            raise Exception("User not authorized for this application")
        
        return {"uid": user.uid, "idToken": auth.create_custom_token(user.uid).decode(), "app_id": app_id}
    except auth.UserNotFoundError:
        raise Exception("User not found")
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")

def register_user(email, password, app_id):
    try:
        user = auth.create_user(email=email, password=password)
        # Initialize user profile in Firestore with app_id for multi-tenancy
        # Use the same credentials as Firebase Admin
        db = firestore_client.Client(project="readrocket-a9268")
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
    try:
        decoded_token = auth.verify_id_token(token)
        if decoded_token["uid"] != user_id:
            raise Exception("Unauthorized")
        
        db = firestore_client.Client(project="readrocket-a9268")
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise Exception("Profile not found")
        
        user_data = user_doc.to_dict()
        
        # Verify user belongs to the requesting app
        if user_data.get("app_id") != app_id:
            raise Exception("User not authorized for this application")
        
        return user_data
    except Exception as e:
        raise Exception(f"Failed to get profile: {str(e)}")

def update_user_profile(user_id, token, preferences, app_id):
    try:
        decoded_token = auth.verify_id_token(token)
        if decoded_token["uid"] != user_id:
            raise Exception("Unauthorized")
        
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
            "preferences": preferences,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        raise Exception(f"Failed to update profile: {str(e)}")

def get_users_by_app(app_id, limit=100):
    """Get all users for a specific app"""
    try:
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

def validate_app_id(app_id):
    """Validate that app_id is in allowed list"""
    ALLOWED_APP_IDS = Config.get_allowed_app_ids()
    
    if app_id not in ALLOWED_APP_IDS:
        raise Exception(f"Invalid app_id: {app_id}. Allowed: {', '.join(ALLOWED_APP_IDS)}")
    
    return True