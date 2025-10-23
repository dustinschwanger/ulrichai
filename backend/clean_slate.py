#!/usr/bin/env python3
"""
Clean slate script - Delete all documents, metadata, and vectors
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from app.core.database import db, supabase
from app.core.vector_store import vector_store
from app.models import DocumentMetadata

# Load environment variables
load_dotenv()

def main():
    print("🧹 Starting clean slate operation...")
    print("=" * 60)

    # 1. Delete all files from Supabase storage
    print("\n1️⃣  Deleting all files from Supabase storage...")
    try:
        if supabase:
            files = supabase.storage.from_('documents').list()
            if files:
                print(f"   Found {len(files)} files in Supabase storage")
                for file_obj in files:
                    filename = file_obj['name']
                    try:
                        supabase.storage.from_('documents').remove([filename])
                        print(f"   ✓ Deleted: {filename}")
                    except Exception as e:
                        print(f"   ✗ Error deleting {filename}: {e}")
                print(f"   ✅ Deleted {len(files)} files from Supabase storage")
            else:
                print("   ℹ️  No files found in Supabase storage")
        else:
            print("   ⚠️  Supabase not configured")
    except Exception as e:
        print(f"   ✗ Error accessing Supabase storage: {e}")

    # 2. Delete all metadata from database
    print("\n2️⃣  Deleting all metadata from database...")
    try:
        session = db.get_session()
        if session:
            count = session.query(DocumentMetadata).count()
            print(f"   Found {count} metadata records in database")
            session.query(DocumentMetadata).delete()
            session.commit()
            print(f"   ✅ Deleted {count} metadata records from database")
            session.close()
        else:
            print("   ⚠️  Database session not available")
    except Exception as e:
        print(f"   ✗ Error deleting metadata from database: {e}")
        if session:
            session.rollback()
            session.close()

    # 3. Delete all vectors from Pinecone
    print("\n3️⃣  Deleting all vectors from Pinecone...")
    try:
        # Get current stats
        stats = vector_store.index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        print(f"   Found {total_vectors} vectors in Pinecone")

        if total_vectors > 0:
            # Delete all vectors by namespace
            namespaces = stats.get('namespaces', {})
            for namespace in namespaces.keys():
                try:
                    vector_store.index.delete(delete_all=True, namespace=namespace)
                    print(f"   ✓ Deleted all vectors from namespace: '{namespace}'")
                except Exception as e:
                    print(f"   ✗ Error deleting namespace {namespace}: {e}")

            # Also delete from default namespace (empty string)
            try:
                vector_store.index.delete(delete_all=True)
                print(f"   ✓ Deleted all vectors from default namespace")
            except Exception as e:
                print(f"   ✗ Error deleting default namespace: {e}")

            print(f"   ✅ Cleaned Pinecone index")
        else:
            print("   ℹ️  No vectors found in Pinecone")

        # Verify cleanup
        stats_after = vector_store.index.describe_index_stats()
        vectors_remaining = stats_after.get('total_vector_count', 0)
        print(f"   📊 Vectors remaining: {vectors_remaining}")

    except Exception as e:
        print(f"   ✗ Error clearing Pinecone: {e}")

    print("\n" + "=" * 60)
    print("✅ Clean slate operation complete!")
    print("\nYou can now upload documents with fresh metadata.")

if __name__ == "__main__":
    response = input("⚠️  This will DELETE ALL documents, metadata, and vectors. Continue? (yes/no): ")
    if response.lower() == 'yes':
        main()
    else:
        print("Cancelled.")
