from flask import Flask, request, jsonify
from firebase_admin import auth, credentials, initialize_app
from auth import authenticate_user, register_user, get_user_profile, update_user_profile
import os

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
initialize_app(cred)

@app.route("/user/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    try:
        user = authenticate_user(email, password)
        return jsonify({"token": user["idToken"], "user_id": user["uid"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/user/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    try:
        user = register_user(email, password)
        return jsonify({"user_id": user["uid"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/user/profile/<user_id>", methods=["GET"])
def profile(user_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]
    try:
        profile = get_user_profile(user_id, token)
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route("/user/profile/<user_id>", methods=["PUT"])
def update_profile(user_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]
    data = request.get_json()
    preferences = data.get("preferences", {})
    try:
        update_user_profile(user_id, token, preferences)
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))