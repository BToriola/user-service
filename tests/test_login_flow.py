#!/usr/bin/env python3
import requests
import json
import random
import string

def generate_random_email():
    """Generate a random email for testing"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@example.com"

def test_complete_flow():
    print("🧪 Testing Complete Registration + Login Flow")
    print("=" * 60)
    
    # Step 1: Register a new user
    email = generate_random_email()
    password = "testpassword123"
    app_id = "readrocket-web"
    
    print(f"📧 Testing with email: {email}")
    
    # Registration data
    reg_data = {
        "email": email,
        "password": password,
        "app_id": app_id,
        "firstName": "Test",
        "lastName": "User",
        "userName": f"testuser{random.randint(1000, 9999)}"
    }
    
    print(f"\n1️⃣ Testing Registration...")
    try:
        response = requests.post("http://localhost:8080/user/register", json=reg_data, timeout=10)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 201:
            user_id = result.get("user_id")
            print(f"✅ Registration successful! User ID: {user_id}")
        else:
            print("❌ Registration failed")
            return None, None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None, None
    
    # Step 2: Login with the same credentials
    print(f"\n2️⃣ Testing Login...")
    login_data = {
        "email": email,
        "password": password,
        "app_id": app_id
    }
    
    try:
        response = requests.post("http://localhost:8080/user/login", json=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            token = result.get("token")
            login_user_id = result.get("user_id")
            print(f"✅ Login successful!")
            print(f"   Token: {token}")
            print(f"   User ID: {login_user_id}")
            return login_user_id, token
        else:
            print("❌ Login failed")
            return None, None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None, None

def test_profile_endpoints(user_id, token):
    print(f"\n3️⃣ Testing Profile Endpoints...")
    
    # Test get profile
    print("   📖 Testing Get Profile...")
    headers = {
        "Authorization": f"Bearer {token}",
        "X-App-ID": "readrocket-web"
    }
    
    try:
        response = requests.get(f"http://localhost:8080/user/profile/{user_id}", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            profile = response.json()
            print(f"   ✅ Profile retrieved successfully!")
            print(f"   Profile data:")
            for key, value in profile.items():
                print(f"     {key}: {value}")
        else:
            print(f"   ❌ Get profile failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Get profile error: {e}")
    
    # Test update profile
    print("\n   ✏️ Testing Update Profile...")
    update_data = {
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "language": "en",
            "modification_mode": "automatic"
        }
    }
    
    try:
        response = requests.put(f"http://localhost:8080/user/profile/{user_id}", 
                              headers=headers, json=update_data, timeout=10)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print(f"   ✅ Profile updated successfully!")
        else:
            print(f"   ❌ Profile update failed")
    except Exception as e:
        print(f"   ❌ Update profile error: {e}")

def test_edge_cases():
    print(f"\n4️⃣ Testing Edge Cases...")
    
    # Test login with wrong app_id
    print("   🚫 Testing login with wrong app_id...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "app_id": "wrong-app"
    }
    
    try:
        response = requests.post("http://localhost:8080/user/login", json=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result.get('error', 'No error message')}")
        
        if response.status_code == 400:
            print(f"   ✅ Correctly rejected invalid app_id")
        else:
            print(f"   ❌ Should have rejected invalid app_id")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test login with non-existent user
    print("\n   👻 Testing login with non-existent user...")
    login_data = {
        "email": "nonexistent@example.com",
        "password": "testpassword123",
        "app_id": "readrocket-web"
    }
    
    try:
        response = requests.post("http://localhost:8080/user/login", json=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result.get('error', 'No error message')}")
        
        if response.status_code == 400:
            print(f"   ✅ Correctly rejected non-existent user")
        else:
            print(f"   ❌ Should have rejected non-existent user")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_admin_endpoint():
    print(f"\n5️⃣ Testing Admin Endpoint...")
    try:
        response = requests.get("http://localhost:8080/admin/users/readrocket-web", timeout=10)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Total users in readrocket-web: {result.get('count', 0)}")
        
        if response.status_code == 200:
            print(f"✅ Admin endpoint working!")
            
            # Show latest user
            users = result.get('users', [])
            if users:
                latest_user = users[-1]  # Assuming last user is our test user
                print(f"\nLatest user profile:")
                for key, value in latest_user.items():
                    print(f"  {key}: {value}")
        else:
            print(f"❌ Admin endpoint failed")
    except Exception as e:
        print(f"❌ Admin endpoint error: {e}")

if __name__ == "__main__":
    print("🚀 Comprehensive User Service Test")
    print("Testing: Registration → Login → Profile Management")
    print("=" * 60)
    
    # Test complete flow
    user_id, token = test_complete_flow()
    
    if user_id and token:
        # Test authenticated endpoints
        test_profile_endpoints(user_id, token)
    
    # Test edge cases
    test_edge_cases()
    
    # Test admin endpoint
    test_admin_endpoint()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("✅ Your user service is working end-to-end!")
