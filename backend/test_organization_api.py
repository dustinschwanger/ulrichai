#!/usr/bin/env python3
"""Test script for LMS organization API endpoints"""

import requests
import json
from uuid import uuid4

# Base URL for the API
BASE_URL = "http://localhost:8000/api/lms/organizations"

def test_organization_api():
    """Test organization CRUD operations via API"""

    print("🧪 Testing LMS Organization API Endpoints...\n")

    # 1. Create a new organization
    print("1️⃣ Creating new organization...")
    org_data = {
        "name": "Test Academy",
        "slug": f"test-academy-{uuid4().hex[:8]}",
        "owner_email": "admin@testacademy.com",
        "settings": {
            "timezone": "America/New_York",
            "language": "en"
        },
        "features": {
            "ai_chat": True,
            "ai_course_builder": True,
            "discussions": True,
            "reflections": True,
            "white_labeling": False
        }
    }

    response = requests.post(BASE_URL, json=org_data)

    if response.status_code == 201:
        org = response.json()
        print(f"✅ Organization created: {org['name']} (ID: {org['id']})")
        org_id = org['id']
    else:
        print(f"❌ Failed to create organization: {response.status_code}")
        print(response.json())
        return

    # 2. Get organization by ID
    print(f"\n2️⃣ Fetching organization by ID: {org_id}...")
    response = requests.get(f"{BASE_URL}/{org_id}")

    if response.status_code == 200:
        org = response.json()
        print(f"✅ Retrieved organization: {org['name']}")
    else:
        print(f"❌ Failed to get organization: {response.status_code}")

    # 3. Get organization by slug
    print(f"\n3️⃣ Fetching organization by slug: {org_data['slug']}...")
    response = requests.get(f"{BASE_URL}/slug/{org_data['slug']}")

    if response.status_code == 200:
        org = response.json()
        print(f"✅ Retrieved organization by slug: {org['name']}")
    else:
        print(f"❌ Failed to get organization by slug: {response.status_code}")

    # 4. Update organization
    print(f"\n4️⃣ Updating organization...")
    update_data = {
        "name": "Updated Test Academy",
        "primary_color": "#FF5733",
        "secondary_color": "#33FF57",
        "settings": {
            "welcome_message": "Welcome to our academy!"
        }
    }

    response = requests.put(f"{BASE_URL}/{org_id}", json=update_data)

    if response.status_code == 200:
        org = response.json()
        print(f"✅ Organization updated: {org['name']}")
        print(f"   Primary color: {org['primary_color']}")
    else:
        print(f"❌ Failed to update organization: {response.status_code}")

    # 5. Update subscription
    print(f"\n5️⃣ Updating subscription to Pro tier...")
    subscription_data = {
        "tier": "pro",
        "max_users": 1000,
        "max_courses": 100
    }

    response = requests.put(f"{BASE_URL}/{org_id}/subscription", json=subscription_data)

    if response.status_code == 200:
        org = response.json()
        print(f"✅ Subscription updated to: {org['subscription_tier']}")
        print(f"   Max users: {org['max_users']}")
        print(f"   Max courses: {org['max_courses']}")
    else:
        print(f"❌ Failed to update subscription: {response.status_code}")

    # 6. Check resource limits
    print(f"\n6️⃣ Checking resource limits...")
    response = requests.get(f"{BASE_URL}/{org_id}/check-limits/users")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ User limit check: {'Within limits' if result['within_limits'] else 'Limit exceeded'}")
    else:
        print(f"❌ Failed to check limits: {response.status_code}")

    # 7. List all organizations
    print(f"\n7️⃣ Listing all organizations...")
    response = requests.get(BASE_URL)

    if response.status_code == 200:
        orgs = response.json()
        print(f"✅ Found {len(orgs)} organization(s)")
        for org in orgs[:5]:  # Show first 5
            print(f"   - {org['name']} ({org['slug']})")
    else:
        print(f"❌ Failed to list organizations: {response.status_code}")

    # 8. Soft delete organization
    print(f"\n8️⃣ Deactivating organization...")
    response = requests.delete(f"{BASE_URL}/{org_id}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Failed to delete organization: {response.status_code}")

    print("\n✨ All tests completed!")

if __name__ == "__main__":
    test_organization_api()