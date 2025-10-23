#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.core.vector_store import vector_store

# Get unique documents from all namespaces
print("DOCUMENTS IN SYSTEM:")
print("="*60)

all_titles = set()

for ns in ['chunks', 'sections', 'documents']:
    result = vector_store.index.query(
        vector=[0.0] * 1024,
        top_k=100,
        include_metadata=True,
        namespace=ns
    )
    for match in result.matches:
        title = match.metadata.get('title') or match.metadata.get('doc_title', 'Unknown')
        all_titles.add(title)

for i, title in enumerate(sorted(all_titles), 1):
    print(f"{i}. {title}")

print(f"\nTotal unique documents: {len(all_titles)}")
