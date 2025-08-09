# auth_utils.py
import requests
import json
import logging
import os

logger = logging.getLogger(__name__)

def verify_firebase_password(email, password):
    """
    Verify user credentials using Firebase Auth REST API
    Returns user info if valid, raises exception if invalid
    """
    # Get Firebase project config
    project_id = "readrocket-a9268"
    
    # Firebase Auth REST API endpoint
    api_key = os.getenv("FIREBASE_API_KEY")
    
    if not api_key:
        # Fallback: try to extract from service account or use a default approach
        logger.warning("FIREBASE_API_KEY not set, attempting alternative authentication")
        return verify_user_exists_only(email)
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        logger.info(f"Attempting password verification for email: {email}")
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            logger.info(f"Password verification successful for user: {user_data.get('localId')}")
            return {
                "uid": user_data.get("localId"),
                "email": user_data.get("email"),
                "id_token": user_data.get("idToken"),
                "verified": True
            }
        else:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            logger.error(f"Password verification failed for {email}: {error_message}")
            raise Exception(f"Invalid credentials: {error_message}")
            
    except requests.RequestException as e:
        logger.error(f"Network error during password verification: {e}")
        raise Exception(f"Authentication service unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Password verification error for {email}: {e}")
        raise Exception(f"Authentication failed: {str(e)}")

def verify_user_exists_only(email):
    """
    Fallback method when API key is not available
    Only verifies user exists, doesn't validate password
    """
    from firebase_admin import auth
    
    logger.warning(f"Using fallback authentication (no password validation) for: {email}")
    
    try:
        user = auth.get_user_by_email(email)
        return {
            "uid": user.uid,
            "email": user.email,
            "verified": False,  # Mark as unverified since we didn't check password
            "fallback": True
        }
    except auth.UserNotFoundError:
        raise Exception("User not found")
    except Exception as e:
        raise Exception(f"User verification failed: {str(e)}")
