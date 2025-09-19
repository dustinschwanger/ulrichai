#!/usr/bin/env python3
"""Test script for LMS authentication API endpoints"""

import requests
import json
from uuid import uuid4

# Base URL for the API
BASE_URL = "http://localhost:8000/api/lms"

def test_auth_flow():
    """Test complete authentication flow"""

    print("🔐 Testing LMS Authentication API...\n")

    # First, get an existing organization (or create one)
    print("0️⃣ Getting test organization...")
    org_response = requests.get(f"{BASE_URL}/organizations/")

    if org_response.status_code == 200:
        orgs = org_response.json()
        if orgs and len(orgs) > 0:
            org_id = orgs[0]['id']
            print(f"✅ Using organization: {orgs[0]['name']} (ID: {org_id})")
        else:
            # Create a test organization
            print("   Creating new test organization...")
            org_data = {
                "name": "Auth Test Organization",
                "slug": f"auth-test-org-{uuid4().hex[:8]}",
                "owner_email": "owner@authtest.com"
            }
            org_create = requests.post(f"{BASE_URL}/organizations/", json=org_data)
            if org_create.status_code == 201:
                org = org_create.json()
                org_id = org['id']
                print(f"✅ Created organization: {org['name']}")
            else:
                print(f"❌ Failed to create organization: {org_create.status_code}")
                return
    else:
        print(f"❌ Failed to get organizations: {org_response.status_code}")
        return

    # 1. Register a new user
    print(f"\n1️⃣ Registering new user...")
    user_data = {
        "email": f"testuser{uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Test",
        "last_name": "User",
        "organization_id": org_id,
        "role": "student",
        "department": "Engineering",
        "job_title": "Software Developer"
    }

    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json=user_data
    )

    if register_response.status_code == 201:
        user = register_response.json()
        print(f"✅ User registered: {user['email']}")
        print(f"   Role: {user['role']}")
        print(f"   Organization ID: {user['organization_id']}")
        user_email = user['email']
    else:
        print(f"❌ Failed to register user: {register_response.status_code}")
        print(register_response.json())
        return

    # 2. Login with the new user (using JSON endpoint)
    print(f"\n2️⃣ Logging in user...")
    login_data = {
        "email": user_email,
        "password": user_data['password']
    }

    login_response = requests.post(
        f"{BASE_URL}/auth/login-json",
        json=login_data
    )

    if login_response.status_code == 200:
        tokens = login_response.json()
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        print(f"✅ Login successful!")
        print(f"   Access token: {access_token[:30]}...")
        print(f"   Refresh token: {refresh_token[:30]}...")
        print(f"   User: {tokens['user']['first_name']} {tokens['user']['last_name']}")
    else:
        print(f"❌ Failed to login: {login_response.status_code}")
        print(login_response.json())
        return

    # 3. Get current user profile
    print(f"\n3️⃣ Getting user profile...")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    profile_response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=headers
    )

    if profile_response.status_code == 200:
        profile = profile_response.json()
        print(f"✅ Retrieved user profile:")
        print(f"   Name: {profile['first_name']} {profile['last_name']}")
        print(f"   Email: {profile['email']}")
        print(f"   Department: {profile['department']}")
    else:
        print(f"❌ Failed to get profile: {profile_response.status_code}")
        print(profile_response.json())

    # 4. Verify token
    print(f"\n4️⃣ Verifying authentication token...")
    verify_response = requests.get(
        f"{BASE_URL}/auth/verify",
        headers=headers
    )

    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        print(f"✅ Token is valid:")
        print(f"   User ID: {verify_data['user_id']}")
        print(f"   Role: {verify_data['role']}")
    else:
        print(f"❌ Failed to verify token: {verify_response.status_code}")

    # 5. Refresh access token
    print(f"\n5️⃣ Refreshing access token...")
    refresh_data = {
        "refresh_token": refresh_token
    }

    refresh_response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json=refresh_data
    )

    if refresh_response.status_code == 200:
        new_tokens = refresh_response.json()
        new_access_token = new_tokens['access_token']
        print(f"✅ Access token refreshed:")
        print(f"   New token: {new_access_token[:30]}...")
    else:
        print(f"❌ Failed to refresh token: {refresh_response.status_code}")

    # 6. Change password
    print(f"\n6️⃣ Changing password...")
    password_data = {
        "old_password": user_data['password'],
        "new_password": "NewSecurePassword456!"
    }

    password_response = requests.put(
        f"{BASE_URL}/auth/me/password",
        json=password_data,
        headers=headers
    )

    if password_response.status_code == 200:
        result = password_response.json()
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Failed to change password: {password_response.status_code}")

    # 7. Test login with new password
    print(f"\n7️⃣ Testing login with new password...")
    new_login_data = {
        "email": user_email,
        "password": "NewSecurePassword456!"
    }

    new_login_response = requests.post(
        f"{BASE_URL}/auth/login-json",
        json=new_login_data
    )

    if new_login_response.status_code == 200:
        print(f"✅ Login with new password successful!")
    else:
        print(f"❌ Failed to login with new password: {new_login_response.status_code}")

    # 8. Register an instructor
    print(f"\n8️⃣ Registering an instructor...")
    instructor_data = {
        "email": f"instructor{uuid4().hex[:8]}@example.com",
        "password": "InstructorPass123!",
        "first_name": "Jane",
        "last_name": "Instructor",
        "organization_id": org_id,
        "role": "instructor",
        "department": "Computer Science",
        "job_title": "Senior Instructor"
    }

    instructor_response = requests.post(
        f"{BASE_URL}/auth/register",
        json=instructor_data
    )

    if instructor_response.status_code == 201:
        instructor = instructor_response.json()
        print(f"✅ Instructor registered: {instructor['email']}")
        print(f"   Role: {instructor['role']}")
    else:
        print(f"❌ Failed to register instructor: {instructor_response.status_code}")

    # 9. Logout
    print(f"\n9️⃣ Logging out...")
    logout_response = requests.post(
        f"{BASE_URL}/auth/logout",
        headers=headers
    )

    if logout_response.status_code == 200:
        result = logout_response.json()
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Failed to logout: {logout_response.status_code}")

    print("\n🎉 All authentication tests completed!")

if __name__ == "__main__":
    test_auth_flow()