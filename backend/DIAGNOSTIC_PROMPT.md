# Comprehensive Diagnostic Prompt for Document Loading Issue

## System Architecture
We have a RAG (Retrieval Augmented Generation) system with the following stack:
- **Backend**: FastAPI (Python)
- **Vector Database**: Pinecone (with namespaces: chunks, sections, documents)
- **File Storage**: Supabase Storage
- **Database**: PostgreSQL (for metadata)
- **Frontend**: React/TypeScript
- **LLM**: OpenAI GPT-4

## Current Problem
When a user asks a question in the chat:
1. ✅ **Search works correctly** - finds the right document with high relevance scores (0.788, 0.758)
2. ✅ **Title displays correctly** - shows "What Makes an Effective HR Function" in the source card
3. ❌ **Wrong document loads** - clicking the source card loads "Agile Orgs_May 2025.pdf" instead

## Critical Log Evidence

### Search Results (WORKING CORRECTLY)
```
2025-10-23 01:09:12,092 - Match 0: score=0.788016319, metadata keys: dict_keys(['chunk_id', 'chunk_text', 'doc_id', 'doc_title', 'section_title'])
2025-10-23 01:09:12,092 - Match 1: score=0.758750916, metadata keys: dict_keys(['chunk_id', 'chunk_text', 'doc_id', 'doc_title', 'section_title'])
```

### Document Viewer Request (BROKEN - EMPTY FILENAME)
```
2025-10-23 01:09:37,096 - app.api.documents - INFO - Requested file:  from bucket: None
2025-10-23 01:09:37,096 - app.api.documents - INFO - Looking for file at: /app/uploads/.pdf
2025-10-23 01:09:37,402 - app.api.documents - INFO - Found fuzzy match: Agile Orgs_May 2025.pdf matches base .pdf
```

**The filename is completely empty!** The request is literally for `.pdf` with no filename.

### Download Endpoint Called With Empty Filename
```
INFO: 100.64.0.2:23308 - "GET /api/ingestion/documents//download HTTP/1.1" 404 Not Found
INFO: 100.64.0.2:23308 - "GET /api/documents/ HTTP/1.1" 307 Temporary Redirect
```

Notice the double slash `//download` indicating missing filename parameter.

## Metadata Format Context

### PDFs in Pinecone (Current Format)
```python
{
    'doc_id': 'a70580d3610106a0692017f662ebf783',
    'doc_title': 'Delivering on Strategic HR Priorities_Feb 2025.pdf',
    'chunk_text': 'CADENCE: REVIEWS,',
    'chunk_id': 'chunk_11',
    'section_title': 'CADENCE: REVIEWS,'
}
```

**Note**: PDFs store the filename in `doc_title`, not in a separate `filename` field!

### Videos in Pinecone (Legacy Format)
```python
{
    'content': 'video transcript text...',
    'title': 'Video Display Name',
    'filename': 'actual_video_file.mp4',  # Has separate filename field
    'section': 'upload',
    'content_type': 'video'
}
```

## Recent Fix Applied
Updated `backend/app/services/chat_service.py` lines 240-257 to extract metadata from both formats:
```python
# Support both PDF and video metadata formats
content = match.metadata.get('content') or match.metadata.get('chunk_text') or match.metadata.get('section_text', '')
title = match.metadata.get('title') or match.metadata.get('doc_title', '')
section = match.metadata.get('section') or match.metadata.get('section_title', '')
```

This creates documents in the format:
```python
{
    'content': 'extracted from chunk_text',
    'title': 'Delivering on Strategic HR Priorities_Feb 2025.pdf',  # from doc_title
    'filename': '',  # EMPTY! No filename in PDF metadata!
    'page_number': '',
    'score': 0.788,
    'chunk_id': 'a70580d3610106a0692017f662ebf783_chunk_11',
    'section': 'CADENCE: REVIEWS,'
}
```

## The Core Issue
**The `filename` field is empty in the search results because PDFs don't have a separate `filename` field in Pinecone metadata - the filename is stored in `doc_title`.**

When this gets passed to the frontend source card, the frontend tries to use the empty `filename` field to load the document, resulting in a request to `/api/documents/.pdf`.

## Files to Investigate

### Backend Search/Chat
1. **`backend/app/services/chat_service.py`**
   - Lines 239-258: Where we build the documents array from search results
   - Lines 268-305: `build_context_prompt` method
   - Lines 130-144: Where sources are formatted for the frontend in `process_query`
   - Lines 342-362: `get_sources_for_query` method

### Backend Document Serving
2. **`backend/app/api/documents.py`**
   - The endpoint that handles `/api/documents/{filename}`
   - How it receives and processes the filename parameter

3. **`backend/app/api/ingestion.py`**
   - Lines with `/download` endpoint
   - How download URLs are generated

### Frontend Source Display
4. **Frontend source card component** (need to find)
   - How it receives source data from the API
   - What field it uses to construct the document viewer URL
   - Where it calls `/api/documents/` or `/api/ingestion/documents/`

## Questions to Answer

1. **In `chat_service.py`**, when building the documents array (lines 247-258), should we:
   - Copy `title` to `filename` when `filename` is empty?
   - Or extract actual filename from `doc_title` (removing .pdf extension for display)?

2. **What does the frontend source card expect?**
   - Does it expect `filename` field?
   - Or `title` field?
   - Or both?

3. **Where is the disconnect happening?**
   - Is the backend returning empty `filename` in the API response?
   - Is the frontend reading the wrong field?
   - Is there a data transformation that's losing the filename?

## Expected Behavior
When returning search results to the frontend, each source should have:
```javascript
{
  "title": "What Makes an Effective HR Function",  // Clean display name
  "filename": "February 2023 Playbook_final.pdf",  // Actual file in Supabase
  "content": "excerpt from the document...",
  "score": 0.788,
  "page_number": "5",
  "section": "Strategic HR Framework"
}
```

## Database Records
We have 7 documents in the `document_metadata` table:
```sql
-- Columns: filename, display_name, document_type, document_source, etc.
```

The `filename` in the database should match the actual file in Supabase Storage.

## Task
Please analyze the complete data flow:
1. **Search Results** → Pinecone returns metadata with `doc_title`
2. **Chat Service** → Builds documents array (currently sets `filename: ''`)
3. **API Response** → Returns sources to frontend
4. **Frontend** → Receives sources and displays them
5. **User Click** → Frontend makes request to load document
6. **Backend** → Receives empty filename, falls back to fuzzy match

**Find where the filename is getting lost and propose a fix that:**
- Preserves the actual filename through the entire chain
- Works for both PDFs (with `doc_title`) and videos (with `filename`)
- Ensures the frontend can load the correct document when a source is clicked

## Additional Context
- The fuzzy matcher is working correctly as a fallback, but we shouldn't need it
- The search is working correctly - finding the right documents
- The title display is working correctly - showing the right title
- Only the document loading is broken due to empty filename
