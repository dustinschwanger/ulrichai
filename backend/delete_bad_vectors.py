#!/usr/bin/env python3
"""
Script to delete vectors for "Module 1-1 Short.mp4" from Pinecone.
This file doesn't exist in Supabase storage anymore, so its vectors are orphaned.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.vector_store import vector_store

def main():
    filename = "Module 1-1 Short.mp4"

    print(f"Deleting all vectors for: {filename}")
    print("This will remove orphaned vectors that don't have corresponding files in storage.")

    try:
        result = vector_store.delete_by_filename(filename)
        print(f"\n✓ Success: {result['message']}")
        print(f"  Filename: {result['filename']}")
        print(f"  Status: {result['status']}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
