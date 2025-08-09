#!/usr/bin/env python3
"""
Simple test script for the deployed user service endpoints
Now that Cloud Run allows unauthenticated access
"""
import requests
import json

# Service URL
SERVICE_URL = "https://rkt-user-service-ae2mdfuq2q-uc.a.run.app"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{SERVICE_URL}/health", timeout=30)
        print(f"✅ Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_register():
    """Test user registration"""
    print("\n👤 Testing user registration...")
    
    headers = {"Content-Type": "application/json"}
    
    data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "app_id": "readrocket-web"
    }
    
    try:
        response = requests.post(f"{SERVICE_URL}/user/register", 
                               headers=headers, 
                               json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return result.get("user_id")
        else:
            print("❌ Registration failed")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_login():
    """Test user login"""
    print("\n🔐 Testing user login...")
    
    headers = {"Content-Type": "application/json"}
    
    data = {
        "email": "test@example.com", 
        "password": "testpassword123",
        "app_id": "readrocket-web"
    }
    
    try:
        response = requests.post(f"{SERVICE_URL}/user/login", 
                               headers=headers, 
                               json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return {
                "token": result.get("token"),
                "user_id": result.get("user_id")
            }
        else:
            print("❌ Login failed")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_get_profile(user_id, firebase_token):
    """Test getting user profile"""
    print(f"\n👤 Testing get profile for user {user_id}...")
    
    headers = {
        "Authorization": f"Bearer {firebase_token}",
        "X-App-ID": "readrocket-web",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{SERVICE_URL}/user/profile/{user_id}", 
                              headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            print("✅ Profile retrieval successful!")
            return True
        else:
            print("❌ Profile retrieval failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_update_profile(user_id, firebase_token):
    """Test updating user profile"""
    print(f"\n✏️ Testing update profile for user {user_id}...")
    
    headers = {
        "Authorization": f"Bearer {firebase_token}",
        "X-App-ID": "readrocket-web",
        "Content-Type": "application/json"
    }
    
    data = {
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "language": "en"
        }
    }
    
    try:
        response = requests.put(f"{SERVICE_URL}/user/profile/{user_id}", 
                              headers=headers,
                              json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            print("✅ Profile update successful!")
            return True
        else:
            print("❌ Profile update failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_admin_endpoint():
    """Test admin endpoint to get users by app"""
    print("\n👑 Testing admin endpoint...")
    
    try:
        response = requests.get(f"{SERVICE_URL}/admin/users/readrocket-web")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            print("✅ Admin endpoint working!")
            return True
        else:
            print("❌ Admin endpoint failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Testing User Service Endpoints")
    print(f"Service URL: {SERVICE_URL}")
    print("=" * 60)
    
    # Test health endpoint
    if not test_health():
        print("❌ Health check failed, stopping tests")
        return
    
    # Test registration
    user_id = test_register()
    if not user_id:
        print("❌ Registration failed, trying login with existing user")
    
    # Test login (works whether user was just created or already exists)
    login_result = test_login()
    if not login_result:
        print("❌ Login failed, cannot test authenticated endpoints")
        return
    
    firebase_token = login_result["token"]
    user_id = login_result["user_id"]
    
    # Test authenticated endpoints
    test_get_profile(user_id, firebase_token)
    test_update_profile(user_id, firebase_token)
    
    # Test admin endpoint
    test_admin_endpoint()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print(f"🔗 Your service is running at: {SERVICE_URL}")

if __name__ == "__main__":
    main()
