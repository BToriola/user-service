#!/usr/bin/env python3
"""
Test script for deployed User Service API
"""

import requests
import json
import time

# Replace this with your actual Cloud Run URL
BASE_URL = "https://your-service-url-here.run.app"

def test_health():
    """Test health endpoint"""
    print("🧪 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_registration():
    """Test user registration"""
    print("\n🧪 Testing user registration...")
    
    unique_email = f"testuser{int(time.time())}@example.com"
    user_data = {
        "email": unique_email,
        "password": "testpassword123",
        "app_id": "readrocket-web"
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
    """Test user login"""
    print("\n🧪 Testing user login...")
    
    login_data = {
        "email": email,
        "password": "testpassword123",
        "app_id": "readrocket-web"
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

def main():
    print("🚀 Testing Deployed User Service")
    print("=" * 50)
    
    # Update BASE_URL before running
    if "your-service-url-here" in BASE_URL:
        print("❌ Please update BASE_URL with your actual Cloud Run URL")
        return
    
    # Test health
    if not test_health():
        print("❌ Health check failed!")
        return
    
    # Test registration
    user_id, email = test_registration()
    if not user_id:
        return
    
    # Test login
    token = test_login(email)
    if not token:
        return
    
    print("\n🎉 All tests passed! Your service is deployed successfully!")

if __name__ == "__main__":
    main()
