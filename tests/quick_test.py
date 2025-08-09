#!/usr/bin/env python3
import requests
import json

SERVICE_URL = "https://rkt-user-service-ae2mdfuq2q-uc.a.run.app"

print("Testing health endpoint...")
try:
    response = requests.get(f"{SERVICE_URL}/health", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")
