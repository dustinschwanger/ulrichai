#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.core.vector_store import vector_store
import openai

# Search for "10 dimensions of HR"
query = "What are the 10 dimensions of an effective HR function?"

# Generate embedding for the query
embedding_response = openai.embeddings.create(
    model="text-embedding-3-large",
    input=query,
    dimensions=1024
)
query_embedding = embedding_response.data[0].embedding

print(f"Searching for: {query}")
print("="*80)

# Search across all namespaces
for ns in ['chunks', 'sections', 'documents']:
    print(f"\nNamespace: {ns}")
    print("-"*80)

    result = vector_store.index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True,
        namespace=ns
    )

    for i, match in enumerate(result.matches):
        print(f"\nMatch {i+1} (score: {match.score:.3f}):")
        doc_title = match.metadata.get('doc_title', match.metadata.get('title', 'Unknown'))
        print(f"  Document: {doc_title[:60]}")

        page_num = match.metadata.get('page_number')
        if page_num:
            print(f"  Page: {page_num}")

        # Get the text content
        text = match.metadata.get('chunk_text') or match.metadata.get('section_text') or match.metadata.get('summary', '')

        # Look for numbered dimensions/items
        import re
        dimensions = re.findall(r'\d+[\.\)]\s*[A-Z][^\.]*', text[:800])
        if dimensions:
            print(f"  Found numbered items: {len(dimensions)}")
            for dim in dimensions[:5]:
                print(f"    - {dim[:70]}")

        # Show a preview
        print(f"  Preview: {text[:200]}...")
