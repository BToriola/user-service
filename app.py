from flask import Flask, request, jsonify
from firebase_admin import auth, credentials, initialize_app
from auth_simple import authenticate_user, register_user, get_user_profile, update_user_profile, validate_app_id
import os
from dotenv import load_dotenv

# Only load .env in development
if os.getenv('GAE_ENV') != 'standard' and os.getenv('GOOGLE_CLOUD_PROJECT') is None:
    load_dotenv()

app = Flask(__name__)

# Initialize Firebase Admin SDK
# In production, use the service account file that's included in the container
service_account_path = "rrkt-firebase-adminsdk.json"
if os.path.exists(service_account_path):
    cred = credentials.Certificate(service_account_path)
elif os.getenv('FIREBASE_CREDENTIALS_PATH'):
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
    # For services like Heroku where we pass JSON as env var
    import json
    cred_dict = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
    cred = credentials.Certificate(cred_dict)
else:
    # Use default credentials as fallback
    cred = credentials.ApplicationDefault()

initialize_app(cred)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "userservice"}), 200

@app.route("/user/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    app_id = data.get("app_id")
    
    if not app_id:
        return jsonify({"error": "app_id is required"}), 400
    
    try:
        validate_app_id(app_id)
        user = authenticate_user(email, password, app_id)
        return jsonify({
            "token": user["idToken"], 
            "user_id": user["uid"],
            "app_id": user["app_id"]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/user/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    app_id = data.get("app_id")
    
    # Optional profile fields (will use defaults if not provided)
    firstName = data.get("firstName")  # Default: email prefix capitalized
    lastName = data.get("lastName")    # Default: "User"
    userName = data.get("userName")    # Default: email prefix
    avatar = data.get("avatar")        # Default: default avatar URL
    
    if not app_id:
        return jsonify({"error": "app_id is required"}), 400
    
    try:
        validate_app_id(app_id)
        user = register_user(email, password, app_id, firstName, lastName, userName, avatar)
        return jsonify({
            "user_id": user["uid"],
            "app_id": user["app_id"],
            "message": "User registered successfully with complete profile"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/user/profile/<user_id>", methods=["GET"])
def profile(user_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401
    
    app_id = request.headers.get("X-App-ID") or request.args.get("app_id")
    if not app_id:
        return jsonify({"error": "app_id is required"}), 400
    
    token = auth_header.split(" ")[1]
    try:
        validate_app_id(app_id)
        profile = get_user_profile(user_id, token, app_id)
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route("/user/profile/<user_id>", methods=["PUT"])
def update_profile(user_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401
    
    app_id = request.headers.get("X-App-ID") or request.args.get("app_id")
    if not app_id:
        return jsonify({"error": "app_id is required"}), 400
    
    token = auth_header.split(" ")[1]
    data = request.get_json()
    preferences = data.get("preferences", {})
    try:
        validate_app_id(app_id)
        update_user_profile(user_id, token, preferences, app_id)
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/admin/users/<app_id>", methods=["GET"])
def get_app_users(app_id):
    """Admin endpoint to get all users for a specific app"""
    # You might want to add admin authentication here
    try:
        validate_app_id(app_id)
        from auth_simple import get_users_by_app
        users = get_users_by_app(app_id)
        return jsonify({
            "app_id": app_id,
            "users": users,
            "count": len(users)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))