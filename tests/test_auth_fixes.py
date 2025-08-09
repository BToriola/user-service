#!/usr/bin/env python3
"""
Test authentication functionality with proper password validation and Firebase path
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_login_with_invalid_password():
    """Test login with invalid password to verify password validation is working"""
    print("\n🔑 Testing login with invalid password...")
    try:
        response = requests.post(f"{BASE_URL}/user/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
            "app_id": "readrocket-web"
        })
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Should fail with 400 due to invalid credentials
        if response.status_code == 400:
            print("✅ Password validation is working (correctly rejected invalid password)")
            return True
        else:
            print("❌ Password validation not working properly")
            return False
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def test_registration():
    """Test user registration"""
    print("\n👤 Testing user registration...")
    test_email = f"testuser_{int(time.time())}@example.com"
    
    try:
        response = requests.post(f"{BASE_URL}/user/register", json={
            "email": test_email,
            "password": "testPassword123",
            "app_id": "readrocket-web",
            "firstName": "Test",
            "lastName": "User"
        })
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration successful")
            return response.json().get("user_id"), test_email
        else:
            print("❌ Registration failed")
            return None, None
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return None, None

def test_login_with_valid_credentials(email, password):
    """Test login with valid credentials"""
    print(f"\n🔓 Testing login with valid credentials for {email}...")
    
    try:
        response = requests.post(f"{BASE_URL}/user/login", json={
            "email": email,
            "password": password,
            "app_id": "readrocket-web"
        })
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login successful")
            return response.json().get("token"), response.json().get("user_id")
        else:
            print("❌ Login failed")
            return None, None
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return None, None

def test_debug_info():
    """Test debug info endpoint"""
    print("\n🐛 Testing debug info endpoint...")
    try:
        # First test without debug mode
        response = requests.get(f"{BASE_URL}/debug/info")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code in [404, 200]  # Either not available or working
    except Exception as e:
        print(f"❌ Debug info test failed: {e}")
        return False

def main():
    print("🚀 Starting comprehensive authentication tests...")
    
    # Test health first
    if not test_health():
        print("❌ Service not available, stopping tests")
        return
    
    # Test invalid password
    test_login_with_invalid_password()
    
    # Test registration
    user_id, test_email = test_registration()
    
    if user_id:
        # Test login with valid credentials
        token, user_id = test_login_with_valid_credentials(test_email, "testPassword123")
        
        if token:
            print(f"✅ Authentication flow working! Token: {token[:20]}...")
    
    # Test debug endpoint
    test_debug_info()
    
    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    main()
