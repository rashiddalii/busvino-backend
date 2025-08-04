import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_register():
    """Test user registration"""
    print("Testing user registration...")
    
    # Generate unique email
    timestamp = int(time.time())
    test_email = f"test{timestamp}@example.com"
    
    payload = {
        "email": test_email,
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "name": "Test User",
        "phone": "+1234567890",
        "location": "Test City",
        "organization_id": "org_zGiETyMerbq4i8c0"
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=payload)
    print(f"Status: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
        
        if response.status_code == 200 and response_json.get("success"):
            print("✅ Registration successful!")
            return response_json.get("data", {}).get("email")
        else:
            print("❌ Registration failed!")
            return None
    except json.JSONDecodeError:
        print(f"❌ Non-JSON response: {response.text}")
        return None

def test_login(email):
    """Test user login"""
    print("Testing user login...")
    
    payload = {
        "email": email,
        "password": "TestPassword123!"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=payload)
    print(f"Status: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
        
        if response.status_code == 200 and response_json.get("success"):
            print("✅ Login successful!")
            return response_json.get("data", {}).get("access_token")
        else:
            print("❌ Login failed!")
            return None
    except json.JSONDecodeError:
        print(f"❌ Non-JSON response: {response.text}")
        return None

def test_protected_route(access_token):
    """Test protected route"""
    print("Testing protected route...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{API_BASE}/auth/protected", headers=headers)
    print(f"Status: {response.status_code}")
    
    try:
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Protected route access successful!")
        else:
            print("❌ Protected route access failed!")
    except json.JSONDecodeError:
        print(f"❌ Non-JSON response: {response.text}")
    
    print("-" * 50)

def main():
    """Run all tests"""
    print("Starting API tests...")
    print("=" * 50)
    
    # Test basic endpoints
    test_root()
    test_health()
    
    # Test authentication flow
    email = test_register()
    if email:
        access_token = test_login(email)
        if access_token:
            test_protected_route(access_token)
    
    print("API tests completed!")

if __name__ == "__main__":
    main() 