#!/usr/bin/env python3
import requests
import json
import random
import string

def generate_random_email():
    """Generate a random email for testing"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@example.com"

def test_local_registration():
    print("🧪 Testing local registration with complete profile...")
    
    # Test 1: Registration with minimal data (should create all required fields)
    email = generate_random_email()
    
    minimal_data = {
        "email": email,
        "password": "testpassword123",
        "app_id": "readrocket-web"
    }
    
    print(f"\n1️⃣ Testing minimal registration for: {email}")
    try:
        response = requests.post("http://localhost:8080/user/register", json=minimal_data, timeout=10)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 201:
            user_id = result.get("user_id")
            print(f"✅ User created with ID: {user_id}")
            return user_id
        else:
            print("❌ Registration failed")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_local_registration_with_fields():
    print("\n🧪 Testing registration with custom fields...")
    
    # Test 2: Registration with custom data
    email = generate_random_email()
    
    full_data = {
        "email": email,
        "password": "testpassword123",
        "app_id": "readrocket-web",
        "firstName": "John",
        "lastName": "Doe",
        "userName": "johndoe",
        "avatar": "https://example.com/custom-avatar.jpg"
    }
    
    print(f"\n2️⃣ Testing full registration for: {email}")
    try:
        response = requests.post("http://localhost:8080/user/register", json=full_data, timeout=10)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 201:
            user_id = result.get("user_id")
            print(f"✅ User created with ID: {user_id}")
            return user_id
        else:
            print("❌ Registration failed")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_admin_endpoint():
    print("\n3️⃣ Checking all users in readrocket-web app...")
    try:
        response = requests.get("http://localhost:8080/admin/users/readrocket-web", timeout=10)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Total users: {result.get('count', 0)}")
        
        # Print detailed user info
        for i, user in enumerate(result.get('users', []), 1):
            print(f"\nUser {i}:")
            for key, value in user.items():
                print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Local User Registration")
    print("=" * 50)
    
    # Test minimal registration
    test_local_registration()
    
    # Test full registration  
    test_local_registration_with_fields()
    
    # Check all users
    test_admin_endpoint()
    
    print("\n" + "=" * 50)
    print("🎉 Local testing completed!")
