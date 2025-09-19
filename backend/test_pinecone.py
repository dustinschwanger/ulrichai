#!/usr/bin/env python3
"""Test Pinecone connectivity and data availability"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone
import openai

load_dotenv()

def test_pinecone():
    """Test Pinecone connection and check for data"""

    print("Testing Pinecone connectivity and data...")
    print("=" * 80)

    # Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment")
        return False

    try:
        pc = Pinecone(api_key=api_key)
        print("✅ Pinecone client initialized")

        # Connect to index
        index_name = os.getenv("PINECONE_INDEX_NAME", "ulrich-ai")
        host = os.getenv("PINECONE_HOST")

        print(f"\nConnecting to index: {index_name}")
        print(f"Host: {host}")

        index = pc.Index(name=index_name, host=host)
        print("✅ Connected to index")

        # Get index stats
        stats = index.describe_index_stats()
        print("\n" + "=" * 80)
        print("INDEX STATISTICS:")
        print(f"Total vectors: {stats.get('total_vector_count', 0)}")
        print(f"Dimension: {stats.get('dimension', 'unknown')}")

        if stats.get('namespaces'):
            print("Namespaces:")
            for ns, ns_stats in stats['namespaces'].items():
                print(f"  - {ns}: {ns_stats.get('vector_count', 0)} vectors")

        # Test query with a sample embedding
        print("\n" + "=" * 80)
        print("TESTING VECTOR SEARCH:")

        # Create a test query
        openai.api_key = os.getenv("OPENAI_API_KEY")
        test_query = "What are the key dimensions of effective leadership?"

        print(f"Test query: {test_query}")

        # Generate embedding
        embedding_response = openai.embeddings.create(
            model="text-embedding-3-large",
            input=test_query,
            dimensions=1024
        )
        query_embedding = embedding_response.data[0].embedding
        print(f"✅ Generated embedding with {len(query_embedding)} dimensions")

        # Search
        search_results = index.query(
            vector=query_embedding,
            top_k=5,
            include_metadata=True
        )

        print(f"\n✅ Search returned {len(search_results.matches)} matches")

        if search_results.matches:
            print("\nTop matches:")
            for i, match in enumerate(search_results.matches, 1):
                print(f"\n{i}. Match:")
                print(f"   Score: {match.score:.4f}")
                print(f"   ID: {match.id}")

                if hasattr(match, 'metadata') and match.metadata:
                    print("   Metadata:")
                    for key, value in match.metadata.items():
                        if key == 'content':
                            print(f"     - {key}: {str(value)[:100]}...")
                        else:
                            print(f"     - {key}: {value}")
                else:
                    print("   No metadata found")
        else:
            print("❌ No matches found!")

        print("\n" + "=" * 80)
        print("✅ Pinecone is working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pinecone()
    if not success:
        print("\n⚠️ Pinecone test failed - check configuration and data")