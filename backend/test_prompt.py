#!/usr/bin/env python3
"""Test script to verify the Dave Ulrich system prompt is working"""

import requests
import json

# API endpoint (Railway backend)
API_URL = "https://ulrichai-production.up.railway.app/api/chat/query"

def test_ulrich_prompt():
    """Test that the backend returns properly formatted Ulrich-style responses"""

    # Test query that should trigger formatted response
    test_query = "What are the key dimensions of effective leadership according to Dave Ulrich?"

    payload = {
        "query": test_query,
        "session_id": "test-session-123"
    }

    print("Testing Dave Ulrich prompt formatting...")
    print(f"Query: {test_query}\n")

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            sources = data.get('sources', [])

            print("Response received successfully!\n")
            print("=" * 80)
            print("ANSWER:")
            print("=" * 80)
            print(answer)
            print("\n" + "=" * 80)

            # Check for formatting elements
            has_bullets = "•" in answer or "-" in answer or "*" in answer
            has_bold = "**" in answer
            has_numbered = any(f"{i}." in answer for i in range(1, 10))

            print("\nFormatting Analysis:")
            print(f"✓ Has bullet points: {has_bullets}")
            print(f"✓ Has bold text: {has_bold}")
            print(f"✓ Has numbered lists: {has_numbered}")

            if sources:
                print(f"\n✓ Found {len(sources)} source(s)")
                for i, source in enumerate(sources, 1):
                    print(f"  {i}. {source.get('title', 'Unknown')} - {source.get('score', 0):.2%} relevance")

            return True

        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_ulrich_prompt()
    print("\n" + "=" * 80)
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed - please check the backend logs")