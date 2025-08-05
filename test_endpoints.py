#!/usr/bin/env python3
"""
Test script for the deployed user service endpoints
"""
import requests
import json
import subprocess
import sys

# Service URL
SERVICE_URL = "https://rkt-user-service-ae2mdfuq2q-uc.a.run.app"

def get_auth_token():
    """Get authentication token for Cloud Run"""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-identity-token"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting auth token: {e}")
        return None

def test_health_endpoint():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{SERVICE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_register_endpoint():
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
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login_endpoint():
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
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            return response.json().get("token")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_without_auth():
    """Test endpoints without authentication to see the exact error"""
    print("\n🚫 Testing without authentication...")
    
    try:
        response = requests.get(f"{SERVICE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response type: {response.headers.get('content-type')}")
        if response.status_code != 200:
            print(f"Error response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("🚀 Testing User Service Endpoints")
    print(f"Service URL: {SERVICE_URL}")
    print("-" * 50)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    if health_ok:
        print("\n✅ Health endpoint working!")
        
        # Test registration
        register_ok = test_register_endpoint()
        if not register_ok:
            print("❌ Registration failed, but will try login anyway (user might already exist)")
        
        # Test login
        user_token = test_login_endpoint()
        
        if user_token:
            print(f"\n✅ Login successful! User token: {user_token[:50]}...")
        else:
            print("\n❌ Login failed")
    else:
        print("\n❌ Health endpoint failed")

if __name__ == "__main__":
    main()
