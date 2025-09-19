#!/usr/bin/env python3
"""Test OpenAI API connectivity"""

import os
from dotenv import load_dotenv
import openai

load_dotenv()

def test_openai():
    """Test OpenAI API key and generation"""

    api_key = os.getenv("OPENAI_API_KEY")
    print(f"Testing OpenAI API...")
    print(f"API Key (first 20 chars): {api_key[:20] if api_key else 'NOT FOUND'}...")

    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False

    try:
        # Set the API key
        openai.api_key = api_key

        # Test with a simple completion
        print("\nTesting chat completion...")

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API is working' if you can hear me."}
            ],
            max_tokens=50,
            temperature=0.5
        )

        answer = response.choices[0].message.content
        print(f"✅ Response received: {answer}")

        # Test embedding generation
        print("\nTesting embedding generation...")
        embedding_response = openai.embeddings.create(
            model="text-embedding-3-large",
            input="Test embedding",
            dimensions=1024
        )

        embedding = embedding_response.data[0].embedding
        print(f"✅ Embedding generated with {len(embedding)} dimensions")

        print("\n✅ OpenAI API is working correctly!")
        return True

    except openai.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("The API key appears to be invalid or expired")
        return False

    except openai.RateLimitError as e:
        print(f"⚠️ Rate Limit Error: {e}")
        print("API key is valid but rate limit exceeded")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_openai()
    if not success:
        print("\n⚠️ OpenAI API test failed - check API key and configuration")