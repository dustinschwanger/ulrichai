#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.core.vector_store import vector_store

# Check if page numbers are in the metadata
print("Checking for page_number in chunk metadata...")
result = vector_store.index.query(
    vector=[0.0] * 1024,
    top_k=5,
    include_metadata=True,
    namespace='chunks'
)

for i, match in enumerate(result.matches):
    print(f"\nMatch {i}:")
    print(f"  ID: {match.id}")
    print(f"  Metadata keys: {list(match.metadata.keys())}")
    print(f"  Has page_number: {'page_number' in match.metadata}")
    if 'page_number' in match.metadata:
        print(f"  Page number: {match.metadata['page_number']}")

    # Show sample of metadata
    print(f"  doc_title: {match.metadata.get('doc_title', 'N/A')[:50]}")
    print(f"  chunk_text preview: {match.metadata.get('chunk_text', 'N/A')[:80]}")
