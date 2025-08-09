from flask import Flask, request, jsonify
from firebase_admin import credentials, initialize_app, storage, firestore
from google.cloud.firestore_v1 import Increment 
from auth_simple import authenticate_user, register_user, get_user_profile, update_user_profile, validate_app_id
from firebase_init import initialize_firebase
from logging_config import setup_logging, log_environment_info, log_request_context, log_performance_metrics, log_security_event
import os
import logging
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
from functools import wraps
# Load environment variables first
load_dotenv()
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env.production')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 

# # Initialize components
# chat_store = ChatStore() 


# Time configuration
WORK_HOURS_START = 9  # 9 AM
WORK_HOURS_END = 18   # 6 PM
TIMEZONE = pytz.timezone("America/Los_Angeles")

# Environment variables
# Firebase setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRED_PATH = os.path.join(BASE_DIR, './rrkt-firebase-adminsdk.json')
PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_PROJECT_ID = PROJECT_ID
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")  
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID') 

def initialize_firebase():
    """Initialize Firebase with credentials if not already initialized"""
    try:
        # Try to get an existing app
        storage.bucket()
        return storage, firestore.client()
    except ValueError:
        # Initialize new app if none exists
        cred = credentials.Certificate(CRED_PATH)
        initialize_app(cred, {
            'storageBucket': 'readrocket-a9268.firebasestorage.app'
        })
        return storage, firestore.client()

# Initialize Firebase
try:
    cred = credentials.Certificate(CRED_PATH)
    initialize_app(cred, {
        'storageBucket': FIREBASE_STORAGE_BUCKET,
        'projectId': PROJECT_ID 
    })
    storage_client = storage.Client()
    firestore_client = firestore.Client()
except Exception as e:
    logger.error(f"Firebase initialization error: {e}")

 


# Set up comprehensive logging
logger = setup_logging("user-service")
log_environment_info()

app = Flask(__name__)

# Middleware for request/response logging
@app.before_request
def log_request_info():
    # Store request start time for performance monitoring
    request.start_time = time.time()
    
    # Log request context
    app_id = request.headers.get("X-App-ID") or request.args.get("app_id")
    auth_header = request.headers.get("Authorization")
    user_id = None
    
    # Try to extract user_id from token for context (simplified extraction)
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        if "user_" in token:
            try:
                user_id = token.split("_")[1]
            except:
                pass
    
    # Log request with context
    log_request_context(request, user_id, app_id)
    
    # Log payload for POST/PUT requests (excluding sensitive data)
    if request.method in ['POST', 'PUT'] and request.is_json:
        try:
            payload = request.get_json()
            if payload:
                # Create a safe copy without sensitive fields
                safe_payload = {k: v for k, v in payload.items() if k not in ['password', 'token']}
                if 'password' in payload:
                    safe_payload['password'] = '[REDACTED]'
                logger.info(f"Request payload: {json.dumps(safe_payload, default=str)}")
        except Exception as e:
            logger.warning(f"Could not parse request payload: {e}")

@app.after_request
def log_response_info(response):
    # Calculate request duration
    duration_ms = (time.time() - getattr(request, 'start_time', time.time())) * 1000
    
    # Log performance metrics
    operation_name = f"{request.method} {request.endpoint or request.path}"
    success = response.status_code < 400
    
    additional_data = {
        'status_code': response.status_code,
        'content_length': response.content_length,
        'path': request.path
    }
    
    log_performance_metrics(operation_name, duration_ms, success, additional_data)
    
    # Log response payload for errors or debug mode
    if response.status_code >= 400:
        try:
            if response.is_json:
                error_data = response.get_json()
                logger.error(f"Error response: {json.dumps(error_data, default=str)}")
        except Exception as e:
            logger.warning(f"Could not parse error response: {e}")
    
    return response

def log_operation(operation_name):
    """Decorator to log function operations with timing"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation_id = f"{operation_name}_{int(start_time * 1000)}"
            
            logger.info(f"Starting operation: {operation_name} [ID: {operation_id}]")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed operation: {operation_name} [ID: {operation_id}] in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed operation: {operation_name} [ID: {operation_id}] after {duration:.3f}s - Error: {str(e)}")
                raise
                
        return wrapper
    return decorator

# Initialize Firebase Admin SDK
try:
    storage, firestore_client = initialize_firebase()
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")
    # Continue without Firebase for now, will fail on first Firebase operation

@app.route("/health", methods=["GET"])
@log_operation("health_check")
def health_check():
    logger.info("Health check requested")
    return jsonify({"status": "healthy", "service": "userservice"}), 200

@app.route("/debug/info", methods=["GET"])
def system_info():
    """Debug endpoint to get system information"""
    if os.getenv('FLASK_DEBUG', 'false').lower() != 'true':
        logger.warning("Debug info endpoint accessed in non-debug mode")
        return jsonify({"error": "Debug endpoint not available"}), 404
    
    try:
        import sys
        import platform
        from datetime import datetime
        
        info = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "environment": {
                "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT", "Not set"),
                "GAE_ENV": os.getenv("GAE_ENV", "Not set"),
                "PORT": os.getenv("PORT", "Not set"),
                "LOG_LEVEL": os.getenv("LOG_LEVEL", "Not set"),
                "ALLOWED_APP_IDS": os.getenv("ALLOWED_APP_IDS", "Not set"),
                "FIREBASE_CREDENTIALS_PATH": "[MASKED]" if os.getenv("FIREBASE_CREDENTIALS_PATH") else "Not set"
            },
            "files": {
                "service_account_exists": os.path.exists("rrkt-firebase-adminsdk.json"),
                "env_file_exists": os.path.exists(".env"),
                "log_file_exists": os.path.exists("user-service.log")
            }
        }
        
        logger.info("System info requested")
        return jsonify(info), 200
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return jsonify({"error": "Failed to get system info"}), 500

@app.route("/user/login", methods=["POST"])
@log_operation("user_login")
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        app_id = data.get("app_id")
        
        logger.info(f"Login attempt for email: {email}, app_id: {app_id}")
        
        # Log security event for login attempt
        log_security_event(
            "login_attempt", 
            email, 
            app_id, 
            {
                "ip": request.remote_addr,
                "user_agent": str(request.user_agent)[:100]
            },
            "INFO"
        )
        
        if not app_id:
            logger.warning("Login failed: app_id is required")
            log_security_event("login_failed", email, app_id, {"reason": "missing_app_id"}, "WARNING")
            return jsonify({"error": "app_id is required"}), 400
        
        validate_app_id(app_id)
        user = authenticate_user(email, password, app_id)
        
        # Log successful login
        log_security_event(
            "login_success", 
            user['uid'], 
            app_id, 
            {
                "ip": request.remote_addr,
                "email": email
            },
            "INFO"
        )
        
        logger.info(f"Login successful for user: {user['uid']}, app_id: {app_id}")
        return jsonify({
            "token": user["idToken"], 
            "user_id": user["uid"],
            "app_id": user["app_id"]
        }), 200
    except Exception as e:
        # Log failed login
        log_security_event(
            "login_failed", 
            email if 'email' in locals() else None, 
            app_id if 'app_id' in locals() else None, 
            {
                "reason": str(e),
                "ip": request.remote_addr
            },
            "WARNING"
        )
        
        logger.error(f"Login failed for email: {email if 'email' in locals() else 'unknown'}, app_id: {app_id if 'app_id' in locals() else 'unknown'} - Error: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route("/user/register", methods=["POST"])
@log_operation("user_register")
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        app_id = data.get("app_id")
        
        # Optional profile fields (will use defaults if not provided)
        firstName = data.get("firstName")  # Default: email prefix capitalized
        lastName = data.get("lastName")    # Default: "User"
        userName = data.get("userName")    # Default: email prefix
        avatar = data.get("avatar")        # Default: default avatar URL
        
        logger.info(f"Registration attempt for email: {email}, app_id: {app_id}")
        
        if not app_id:
            logger.warning("Registration failed: app_id is required")
            return jsonify({"error": "app_id is required"}), 400
        
        validate_app_id(app_id)
        user = register_user(email, password, app_id, firstName, lastName, userName, avatar)
        
        logger.info(f"Registration successful for user: {user['uid']}, app_id: {app_id}")
        return jsonify({
            "user_id": user["uid"],
            "app_id": user["app_id"],
            "message": "User registered successfully with complete profile"
        }), 201
    except Exception as e:
        logger.error(f"Registration failed for email: {email if 'email' in locals() else 'unknown'}, app_id: {app_id if 'app_id' in locals() else 'unknown'} - Error: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route("/user/profile/<user_id>", methods=["GET"])
@log_operation("get_user_profile")
def profile(user_id):
    try:
        auth_header = request.headers.get("Authorization")
        app_id = request.headers.get("X-App-ID") or request.args.get("app_id")
        
        logger.info(f"Profile request for user_id: {user_id}, app_id: {app_id}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Profile request failed for user_id: {user_id} - Missing or invalid token")
            return jsonify({"error": "Missing or invalid token"}), 401
        
        if not app_id:
            logger.warning(f"Profile request failed for user_id: {user_id} - app_id is required")
            return jsonify({"error": "app_id is required"}), 400
        
        token = auth_header.split(" ")[1]
        validate_app_id(app_id)
        profile = get_user_profile(user_id, token, app_id)
        
        logger.info(f"Profile retrieved successfully for user_id: {user_id}, app_id: {app_id}")
        return jsonify(profile), 200
    except Exception as e:
        logger.error(f"Profile retrieval failed for user_id: {user_id}, app_id: {app_id if 'app_id' in locals() else 'unknown'} - Error: {str(e)}")
        return jsonify({"error": str(e)}), 401

@app.route("/user/profile/<user_id>", methods=["PUT"])
@log_operation("update_user_profile")
def update_profile(user_id):
    try:
        auth_header = request.headers.get("Authorization")
        app_id = request.headers.get("X-App-ID") or request.args.get("app_id")
        data = request.get_json()
        preferences = data.get("preferences", {}) if data else {}
        
        logger.info(f"Profile update request for user_id: {user_id}, app_id: {app_id}, preferences: {preferences}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Profile update failed for user_id: {user_id} - Missing or invalid token")
            return jsonify({"error": "Missing or invalid token"}), 401
        
        if not app_id:
            logger.warning(f"Profile update failed for user_id: {user_id} - app_id is required")
            return jsonify({"error": "app_id is required"}), 400
        
        token = auth_header.split(" ")[1]
        validate_app_id(app_id)
        update_user_profile(user_id, token, preferences, app_id)
        
        logger.info(f"Profile updated successfully for user_id: {user_id}, app_id: {app_id}")
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        logger.error(f"Profile update failed for user_id: {user_id}, app_id: {app_id if 'app_id' in locals() else 'unknown'} - Error: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route("/admin/users/<app_id>", methods=["GET"])
@log_operation("get_app_users")
def get_app_users(app_id):
    """Admin endpoint to get all users for a specific app"""
    try:
        logger.info(f"Admin request to get users for app_id: {app_id}")
        
        # You might want to add admin authentication here
        validate_app_id(app_id)
        from auth_simple import get_users_by_app
        users = get_users_by_app(app_id)
        
        logger.info(f"Retrieved {len(users)} users for app_id: {app_id}")
        return jsonify({
            "app_id": app_id,
            "users": users,
            "count": len(users)
        }), 200
    except Exception as e:
        logger.error(f"Failed to get users for app_id: {app_id} - Error: {str(e)}")
        return jsonify({"error": str(e)}), 400

# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url} not found")
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: Internal server error - {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting Flask application on port {port}")
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")