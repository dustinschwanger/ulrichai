#!/usr/bin/env python3
"""
Test script to verify LMS frontend-backend integration
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/lms"

def test_frontend_backend_integration():
    """Test the complete authentication flow"""

    print("Testing LMS Frontend-Backend Integration")
    print("-" * 40)

    # Test 1: Create an organization first
    print("\n1. Creating test organization...")
    org_data = {
        "name": "Test University",
        "slug": f"test-uni-{int(time.time())}",
        "owner_email": f"admin.{int(time.time())}@testuni.edu",
        "primary_color": "#0066CC",
        "secondary_color": "#FF6600"
    }

    try:
        org_response = requests.post(f"{BASE_URL}/organizations", json=org_data)
        print(f"   Debug: Status code: {org_response.status_code}")
        if org_response.status_code in [200, 201]:
            org = org_response.json()
            if "id" in org:
                org_id = org["id"]
                print(f"   ✓ Organization created: {org['name']} (ID: {org_id})")
            else:
                print(f"   ✗ Unexpected response format: {org}")
                return
        else:
            # Try to get existing organization
            orgs = requests.get(f"{BASE_URL}/organizations").json()
            if orgs and "organizations" in orgs and len(orgs["organizations"]) > 0:
                org_id = orgs["organizations"][0]["id"]
                print(f"   ✓ Using existing organization (ID: {org_id})")
            else:
                print(f"   ✗ Failed to create organization: {org_response.text}")
                return
    except Exception as e:
        print(f"   ✗ Error creating organization: {e}")
        return

    # Test 2: Register a new user
    print("\n2. Registering new user...")
    user_data = {
        "email": f"test.user.{int(time.time())}@example.com",
        "password": "Test123456!",
        "first_name": "Test",
        "last_name": "User",
        "organization_id": org_id,
        "role": "student",
        "department": "Engineering",
        "job_title": "Software Developer"
    }

    try:
        reg_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"   Debug: Registration status code: {reg_response.status_code}")
        if reg_response.status_code in [200, 201]:
            response_data = reg_response.json()
            # Check if it's an auth response with tokens or just user data
            if "access_token" in response_data:
                auth_data = response_data
                print(f"   ✓ User registered: {user_data['email']}")
                print(f"   ✓ Access token received: {auth_data['access_token'][:20]}...")
            elif "id" in response_data and "email" in response_data:
                # Registration successful but no token returned - need to login
                print(f"   ✓ User registered: {response_data['email']}")
                print(f"   Note: No access token returned, will need to login")
            else:
                print(f"   ✗ Unexpected registration response: {response_data}")
                return
        else:
            print(f"   ✗ Registration failed: {reg_response.text}")
            return
    except Exception as e:
        print(f"   ✗ Error registering user: {e}")
        return

    # Test 3: Login with the new user
    print("\n3. Testing login...")
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }

    try:
        # Use the JSON login endpoint instead of form-based endpoint
        login_response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data)
        print(f"   Debug: Login status code: {login_response.status_code}")
        if login_response.status_code == 200:
            auth_data = login_response.json()
            if "access_token" in auth_data:
                access_token = auth_data["access_token"]
                print(f"   ✓ Login successful")
                if "user" in auth_data:
                    print(f"   ✓ User role: {auth_data['user']['role']}")
            else:
                print(f"   ✗ No access token in login response: {auth_data}")
                return
        else:
            print(f"   ✗ Login failed: {login_response.text}")
            return
    except Exception as e:
        print(f"   ✗ Error logging in: {e}")
        return

    # Test 4: Get user profile
    print("\n4. Getting user profile...")
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        profile_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if profile_response.status_code == 200:
            profile = profile_response.json()
            print(f"   ✓ Profile retrieved: {profile['first_name']} {profile['last_name']}")
            print(f"   ✓ Organization ID: {profile['organization_id']}")
        else:
            print(f"   ✗ Failed to get profile: {profile_response.text}")
    except Exception as e:
        print(f"   ✗ Error getting profile: {e}")

    # Test 5: Check frontend accessibility
    print("\n5. Checking frontend pages...")
    frontend_urls = [
        ("http://localhost:3001/lms/login", "Login Page"),
        ("http://localhost:3001/lms/register", "Registration Page"),
        ("http://localhost:3001/lms/dashboard", "Dashboard (should redirect)")
    ]

    for url, name in frontend_urls:
        try:
            response = requests.get(url, timeout=5)
            status = "✓" if response.status_code == 200 else "✗"
            print(f"   {status} {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ✗ {name}: Could not connect")

    print("\n" + "=" * 40)
    print("✅ Frontend-Backend Integration Test Complete!")
    print(f"You can now access the LMS at: http://localhost:3001")
    print(f"Login with: {user_data['email']} / {user_data['password']}")
    print("=" * 40)

if __name__ == "__main__":
    test_frontend_backend_integration()