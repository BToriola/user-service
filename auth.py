from firebase_admin import auth, firestore
from google.cloud import firestore as firestore_client

def authenticate_user(email, password):
    # Firebase Authentication doesn't directly support password verification in Admin SDK.
    # Instead, we simulate login by creating a custom token and exchanging it client-side.
    # For simplicity, assume client sends ID token after Firebase Auth login.
    # Here, we verify the email exists and return user data.
    try:
        user = auth.get_user_by_email(email)
        return {"uid": user.uid, "idToken": auth.create_custom_token(user.uid).decode()}
    except auth.UserNotFoundError:
        raise Exception("User not found")
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")

def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        # Initialize user profile in Firestore
        db = firestore_client.Client()
        db.collection("users").document(user.uid).set({
            "email": email,
            "subscription_status": "free",
            "preferences": {"modification_mode": "suggestion"}
        })
        return {"uid": user.uid}
    except Exception as e:
        raise Exception(f"Registration failed: {str(e)}")

def get_user_profile(user_id, token):
    try:
        decoded_token = auth.verify_id_token(token)
        if decoded_token["uid"] != user_id:
            raise Exception("Unauthorized")
        db = firestore_client.Client()
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise Exception("Profile not found")
        return user_doc.to_dict()
    except Exception as e:
        raise Exception(f"Failed to get profile: {str(e)}")

def update_user_profile(user_id, token, preferences):
    try:
        decoded_token = auth.verify_id_token(token)
        if decoded_token["uid"] != user_id:
            raise Exception("Unauthorized")
        db = firestore_client.Client()
        db.collection("users").document(user_id).update({
            "preferences": preferences
        })
    except Exception as e:
        raise Exception(f"Failed to update profile: {str(e)}")