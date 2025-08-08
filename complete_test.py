#!/usr/bin/env python3
import requests
import json
import random
import string

SERVICE_URL = "https://rkt-user-service-ae2mdfuq2q-uc.a.run.app"

def generate_random_email():
    """Generate a random email for testing"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@example.com"

def test_registration_and_login():
    print("🧪 Testing registration and login flow...")
    
    # Generate unique email
    email = generate_random_email()
    password = "testpassword123"
    app_id = "readrocket-web"
    
    print(f"📧 Using email: {email}")
    
    # Test registration
    print("\n1️⃣ Testing registration...")
    reg_data = {
        "email": email,
        "password": password,
        "app_id": app_id
    }
    
    try:
        response = requests.post(f"{SERVICE_URL}/user/register", json=reg_data, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            user_id = response.json().get("user_id")
            print(f"✅ Registration successful! User ID: {user_id}")
            
            # Test login
            print("\n2️⃣ Testing login...")
            login_data = {
                "email": email,
                "password": password,
                "app_id": app_id
            }
            
            response = requests.post(f"{SERVICE_URL}/user/login", json=login_data, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                token = response.json().get("token")
                print(f"✅ Login successful! Token: {token[:20]}...")
                return user_id, token
            else:
                print("❌ Login failed")
                return None, None
        else:
            print("❌ Registration failed")
            return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def test_profile_endpoints(user_id, token):
    print(f"\n3️⃣ Testing profile endpoints for user {user_id}...")
    
    # Test get profile
    headers = {
        "Authorization": f"Bearer {token}",
        "X-App-ID": "readrocket-web"
    }
    
    try:
        response = requests.get(f"{SERVICE_URL}/user/profile/{user_id}", headers=headers, timeout=30)
        print(f"Get Profile Status: {response.status_code}")
        print(f"Get Profile Response: {response.json()}")
        
        # Test update profile
        update_data = {
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        response = requests.put(f"{SERVICE_URL}/user/profile/{user_id}", 
                              headers=headers, json=update_data, timeout=30)
        print(f"Update Profile Status: {response.status_code}")
        print(f"Update Profile Response: {response.json()}")
        
    except Exception as e:
        print(f"❌ Error testing profile: {e}")

def test_admin_endpoint():
    print("\n4️⃣ Testing admin endpoint...")
    try:
        response = requests.get(f"{SERVICE_URL}/admin/users/readrocket-web", timeout=30)
        print(f"Admin Status: {response.status_code}")
        result = response.json()
        print(f"Admin Response: {result}")
        print(f"Total users: {result.get('count', 0)}")
    except Exception as e:
        print(f"❌ Error testing admin: {e}")

if __name__ == "__main__":
    print("🚀 Complete User Service Test")
    print("=" * 50)
    
    # Test full flow
    user_id, token = test_registration_and_login()
    
    if user_id and token:
        test_profile_endpoints(user_id, token)
    
    test_admin_endpoint()
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
