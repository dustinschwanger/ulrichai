#!/usr/bin/env python3
"""Test script to check if API returns sources"""

import requests
import json

# API endpoint
API_URL = "https://ulrichai-production.up.railway.app/api/chat/query"

def test_api_sources():
    """Test that the API returns sources with the response"""

    test_query = "What are the key dimensions of effective leadership according to Dave Ulrich?"

    payload = {
        "query": test_query,
        "session_id": "test-sources-123"
    }

    print("Testing API sources response...")
    print(f"Query: {test_query}\n")

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()

            print("✅ API Response received\n")
            print("=" * 80)

            # Check if sources exist
            has_sources = 'sources' in data
            print(f"Has 'sources' field: {has_sources}")

            if has_sources:
                sources = data.get('sources', [])
                print(f"Number of sources: {len(sources)}")

                if sources:
                    print("\nSources found:")
                    for i, source in enumerate(sources, 1):
                        print(f"\n{i}. Source:")
                        print(f"   - Title: {source.get('title', 'N/A')}")
                        print(f"   - Filename: {source.get('filename', 'N/A')}")
                        print(f"   - Score: {source.get('score', 0):.2%}")
                        print(f"   - Section: {source.get('section', 'N/A')}")
                        print(f"   - Page: {source.get('page_number', 'N/A')}")
                        print(f"   - Content preview: {source.get('content', '')[:100]}...")
                else:
                    print("⚠️ Sources array is empty!")
            else:
                print("❌ No 'sources' field in response!")

            # Show the full response structure
            print("\n" + "=" * 80)
            print("Full response structure:")
            print(json.dumps(data, indent=2))

        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_sources()