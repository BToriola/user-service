#!/usr/bin/env python3
"""
Test script for the User Service API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_registration():
    """Test user registration endpoint"""
    print("🧪 Testing user registration...")
    
    import time
    unique_email = f"testuser{int(time.time())}@example.com"
    
    user_data = {
        "email": unique_email,
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/user/register", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        print("✅ Registration successful!")
        return response.json().get("user_id"), unique_email
    else:
        print("❌ Registration failed!")
        return None, None

def test_login(email):
    """Test user login endpoint"""
    print("\n🧪 Testing user login...")
    
    login_data = {
        "email": email,
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/user/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        return response.json().get("token")
    else:
        print("❌ Login failed!")
        return None

def test_get_profile(user_id, token):
    """Test get user profile endpoint"""
    print(f"\n🧪 Testing get user profile for user_id: {user_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/user/profile/{user_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Get profile successful!")
    else:
        print("❌ Get profile failed!")

def test_update_profile(user_id, token):
    """Test update user profile endpoint"""
    print(f"\n🧪 Testing update user profile for user_id: {user_id}...")
    
    update_data = {
        "preferences": {
            "modification_mode": "direct",
            "theme": "dark"
        }
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/user/profile/{user_id}", json=update_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Update profile successful!")
    else:
        print("❌ Update profile failed!")

def main():
    print("🚀 Starting User Service API Tests")
    print("=" * 50)
    
    # Test registration
    user_id, email = test_registration()
    if not user_id:
        print("Registration failed, stopping tests.")
        return
    
    # Test login
    token = test_login(email)
    if not token:
        print("Login failed, stopping tests.")
        return
    
    # Test get profile
    test_get_profile(user_id, token)
    
    # Test update profile
    test_update_profile(user_id, token)
    
    # Test get profile again to see updates
    print("\n🧪 Testing get profile again to verify updates...")
    test_get_profile(user_id, token)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()
