# backend/app/services/chat_service.py

from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
import os
import logging
import json
from datetime import datetime
import re

from ..core.vector_store import vector_store
from ..core.database import db

load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

class DocumentNameMapper:
    """
    Helper class for mapping file names to display names.
    """
    
    @classmethod
    def get_display_name(cls, filename: str) -> str:
        """Get a clean display name for a document."""
        if not filename:
            return "Unknown Document"
        
        # Remove timestamp prefix if present (format: YYYYMMDD_HHMMSS_)
        if re.match(r'^\d{8}_\d{6}_', filename):
            filename = re.sub(r'^\d{8}_\d{6}_', '', filename)
        
        # Remove extension
        name = filename.rsplit('.', 1)[0]
        
        # Replace underscores and hyphens with spaces
        name = name.replace('_', ' ').replace('-', ' ')
        
        # Handle CamelCase
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split())
        
        # Handle common abbreviations
        abbreviations = {
            'Hr': 'HR', 'Ai': 'AI', 'Ml': 'ML', 'Rbl': 'RBL',
            'Kpi': 'KPI', 'Roi': 'ROI', 'Ceo': 'CEO', 'Cfo': 'CFO',
            'Cto': 'CTO', 'Vp': 'VP', 'Svp': 'SVP', 'Evp': 'EVP'
        }
        
        for abbr, replacement in abbreviations.items():
            name = name.replace(abbr, replacement)
        
        return name

class ChatService:
    def _format_document_source(self, source: str) -> str:
        """Convert technical document source to user-friendly display name"""
        if not source:
            return "Main Content"
        
        # Define mappings for common sources
        source_mappings = {
            'dave-ulrich-hr-academy': 'Dave Ulrich HR Academy',
            'institute': 'RBL Institute',
            'rbl-institute': 'RBL Institute',
            'external': 'External Source',
            'case-study': 'Case Study',
            'white-paper': 'White Paper',
            'research': 'Research',
            'blog': 'Blog',
            'article': 'Article',
            'playbook': 'Playbook',
            'toolkit': 'Toolkit'
        }
        
        # Check for exact match first
        if source.lower() in source_mappings:
            return source_mappings[source.lower()]
        
        # If no exact match, format the string nicely
        # Replace hyphens and underscores with spaces, then title case
        formatted = source.replace('-', ' ').replace('_', ' ')
        return ' '.join(word.capitalize() for word in formatted.split())

    def __init__(self):
        self.max_context_docs = 5
        self.max_context_chunks = 10
        self.name_mapper = DocumentNameMapper()
        
    async def process_query(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a user query using Sandusky Current's approach"""
        
        try:
            logger.info(f"Processing query: {query}")
            
            # Search for context (like Sandusky) - increased to get more comprehensive results
            search_results = await self.search_context(query, limit=10)
            
            # Build context prompt (like Sandusky)
            context_prompt = self.build_context_prompt(search_results)
            
            # Create the full prompt for OpenAI
            full_prompt = f"""Based on the following context, please provide a comprehensive answer about HR and organizational development.

{context_prompt}

Question: {query}

IMPORTANT INSTRUCTIONS:
1. Present information with the authoritative confidence of Dave Ulrich's decades of organizational research
2. Extract frameworks, dimensions, and lists exactly as they appear in the source materials
3. Use Dave Ulrich's direct, business-focused communication style - no hedging or tentative language
4. Structure responses with clear frameworks and practical applications
5. Focus on actionable insights that drive organizational effectiveness
6. Avoid phrases like "However, this may not be complete" or "additional factors may exist"

Provide a comprehensive, authoritative response in Dave Ulrich's voice based on the context above."""
            
            # Generate response using OpenAI
            response = await self.generate_response(full_prompt)
            
            # Format sources for frontend
            sources = []
            for doc in search_results.get('documents', [])[:4]:  # Limit to 4 like original
                raw_section = doc.get('section', '')
                formatted_section = self._format_document_source(raw_section)
                
                sources.append({
                    "title": doc.get('title', ''),
                    "filename": doc.get('filename', ''),
                    "content": doc.get('content', '')[:200],  # Preview
                    "score": doc.get('score', 0.0),
                    "page_number": doc.get('page_number'),
                    "section": formatted_section,
                    "type": "chunk",
                    "start_time": doc.get('start_time'),
                    "end_time": doc.get('end_time')
                })
            
            formatted_response = {
                "answer": response,
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log analytics
            await self.log_analytics(query, formatted_response, session_id)
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your question. Please try again.",
                "sources": [],
                "error": str(e)
            }
    
    async def search_context(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Enhanced search with sequential chunk retrieval for structured content"""
        
        logger.info(f"Searching context for query: {query}")
        
        try:
            # Generate query embedding using OpenAI
            embedding_response = openai.embeddings.create(
                model="text-embedding-3-large",
                input=query,
                dimensions=1024
            )
            query_embedding = embedding_response.data[0].embedding
            logger.info(f"Generated embedding with {len(query_embedding)} dimensions")
            
            # Search documents using Pinecone
            index = vector_store.index
            
            # Debug: Log index stats
            index_stats = index.describe_index_stats()
            logger.info(f"Index stats: {index_stats}")
            
            search_results = index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True
            )
            
            # Debug: Log what we got back from search
            logger.info(f"Search returned {len(search_results.matches)} matches")
            for i, match in enumerate(search_results.matches[:2]):  # Log first 2 matches
                logger.info(f"Match {i}: score={match.score}, metadata keys: {match.metadata.keys()}")
                if match.metadata.get('content_type') == 'video':
                    logger.info(f"Video match - start_time: {match.metadata.get('start_time')}, end_time: {match.metadata.get('end_time')}")
            
            # Debug: Log search results
            logger.info(f"Raw search results: {len(search_results.matches) if search_results.matches else 0} matches")
            
            # Format results and detect if this is a structured query
            documents = []
            if search_results.matches:
                # Check if this appears to be asking for structured content
                is_structured_query = self._is_structured_query(query)
                
                for match in search_results.matches:
                    documents.append({
                        'content': match.metadata.get('content', ''),
                        'title': match.metadata.get('title', ''),
                        'filename': match.metadata.get('filename', ''),
                        'page_number': match.metadata.get('page_number', ''),
                        'score': float(match.score) if hasattr(match, 'score') else 0.0,
                        'chunk_id': match.id if hasattr(match, 'id') else None,
                        'start_time': match.metadata.get('start_time'),
                        'end_time': match.metadata.get('end_time'),
                        'content_type': match.metadata.get('content_type'),
                        'section': match.metadata.get('section', '')
                    })
                
                # If structured query, get sequential chunks from best matches
                if is_structured_query and documents:
                    logger.info("Detected structured query - fetching sequential chunks")
                    documents = await self._get_sequential_chunks(documents, index)
            
            logger.info(f"Found {len(documents)} relevant documents (including sequential chunks)")
            
            return {
                'documents': documents
            }
            
        except Exception as e:
            logger.error(f"Error in search_context: {e}")
            return {'documents': []}
    
    def build_context_prompt(self, search_results: Dict[str, Any]) -> str:
        """Build context prompt using Sandusky Current's approach"""
        
        context_parts = []
        
        # Add relevant documents
        documents = search_results.get('documents', [])
        if documents:
            context_parts.append("**RELEVANT DOCUMENTS:**")
            for doc in documents:
                title = doc.get('title', 'Unknown Document')
                content = doc.get('content', '')[:800]  # Increased from 500 for better context
                page_num = doc.get('page_number', '')
                
                doc_info = f"- **{title}**"
                if page_num:
                    doc_info += f" (Page {page_num})"
                doc_info += f": {content}"
                
                context_parts.append(doc_info)
            
            context_parts.append("")  # Add spacing
        
        return "\n".join(context_parts) if context_parts else ""
    
    async def get_graph_context(self, doc_id: str) -> List[str]:
        """Get related documents from the graph"""
        
        try:
            from ..processing.graph_builder import graph_builder
            
            # Get related documents
            related = graph_builder.find_related_documents(doc_id, max_docs=3)
            
            # Fetch their summaries
            related_summaries = []
            if related and db.engine:
                from sqlalchemy import text
                
                with db.engine.connect() as conn:
                    for rel_doc_id, weight in related:
                        result = conn.execute(
                            text("SELECT display_name, description FROM admin_documents WHERE id = :id"),
                            {'id': rel_doc_id}
                        )
                        row = result.first()
                        if row:
                            related_summaries.append({
                                'title': row.display_name,
                                'summary': row.description[:200] if row.description else '',
                                'relevance': weight
                            })
            
            return related_summaries
            
        except Exception as e:
            logger.error(f"Error getting graph context: {e}")
            return []
    
    
    async def get_sources_for_query(self, query: str) -> List[Dict[str, Any]]:
        """Get sources for a query without generating response"""
        try:
            search_results = await self.search_context(query, limit=10)
            sources = []
            for doc in search_results.get('documents', [])[:4]:
                raw_section = doc.get('section', '')
                formatted_section = self._format_document_source(raw_section)

                sources.append({
                    "title": doc.get('title', ''),
                    "filename": doc.get('filename', ''),
                    "content": doc.get('content', '')[:200],
                    "score": doc.get('score', 0.0),
                    "page_number": doc.get('page_number'),
                    "section": formatted_section,
                    "type": "chunk",
                    "start_time": doc.get('start_time'),
                    "end_time": doc.get('end_time')
                })
            return sources
        except Exception as e:
            logger.error(f"Error getting sources: {e}")
            return []

    async def process_query_stream(self, query: str, session_id: Optional[str] = None):
        """Process query with streaming response"""
        try:
            logger.info(f"Processing streaming query: {query}")

            # Search for context
            search_results = await self.search_context(query, limit=10)
            context_prompt = self.build_context_prompt(search_results)

            # Create the full prompt
            full_prompt = f"""Based on the following context, please provide a comprehensive answer about HR and organizational development.

{context_prompt}

Question: {query}

IMPORTANT INSTRUCTIONS:
1. Present information with the authoritative confidence of Dave Ulrich's decades of organizational research
2. Extract frameworks, dimensions, and lists exactly as they appear in the source materials
3. Use Dave Ulrich's direct, business-focused communication style - no hedging or tentative language
4. Structure responses with clear frameworks and practical applications
5. Focus on actionable insights that drive organizational effectiveness
6. Avoid phrases like "However, this may not be complete" or "additional factors may exist"

Provide a comprehensive, authoritative response in Dave Ulrich's voice based on the context above."""

            # Import the enhanced Ulrich system prompt
            from ..prompts.ulrich_system_prompt import ULRICH_SYSTEM_PROMPT

            # Use async streaming
            import openai as openai_module
            client = openai_module.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response_stream = await client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1500,
                messages=[
                    {
                        "role": "system",
                        "content": ULRICH_SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                temperature=0.7,
                stream=True
            )

            # Yield chunks as they come
            async for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            # Log analytics
            await self.log_analytics(query, {"streaming": True}, session_id)

        except Exception as e:
            logger.error(f"Error in streaming query: {e}")
            yield "I apologize, but I'm having trouble generating a response. Please try again."

    async def generate_response(self, prompt: str) -> str:
        """Generate response using OpenAI"""

        try:
            # Import the enhanced Ulrich system prompt
            from ..prompts.ulrich_system_prompt import ULRICH_SYSTEM_PROMPT

            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # Use GPT-4o-mini for faster responses
                max_tokens=1500,
                messages=[
                    {
                        "role": "system",
                        "content": ULRICH_SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    def format_sources_enhanced(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format source references with enhanced metadata including file URLs - LIMITED TO 4"""
        
        sources = []
        seen_combinations = set()
        
        # Process chunks first (most specific) - limit to 4
        for chunk in context_data.get("chunks", [])[:4]:
            # Extract metadata
            metadata = chunk.metadata if hasattr(chunk, 'metadata') else {}
            
            # Get filename and title
            doc_filename = metadata.get('filename', '') or metadata.get('document_name', '')
            doc_title = metadata.get('title', '') or metadata.get('display_name', '')
            
            # Get other metadata
            raw_section = metadata.get('section', '')
            section_title = self._format_document_source(raw_section)
            page_num = metadata.get('page_number')
            file_url = metadata.get('file_url', '')
            
            # Create unique identifier to avoid duplicates (use raw section for consistency)
            source_key = f"{doc_filename}_{raw_section}_{page_num}"
            if source_key in seen_combinations:
                continue
            seen_combinations.add(source_key)
            
            # Use title if available, otherwise clean filename
            display_name = doc_title if doc_title else self.name_mapper.get_display_name(doc_filename)
            
            # Generate a concise relevance summary
            content_preview = metadata.get('content', '')
            relevance_summary = self._generate_relevance_summary(content_preview, section_title)
            
            start_time = metadata.get('start_time')
            end_time = metadata.get('end_time')
            content_type = metadata.get('content_type')
            
            logger.info(f"Processing source - filename: {doc_filename}, content_type: {content_type}, start_time: {start_time}, end_time: {end_time}")
            
            sources.append({
                "title": display_name,
                "filename": doc_filename,
                "content": relevance_summary,
                "score": float(chunk.score) if hasattr(chunk, 'score') else 0.85,
                "chunk_id": chunk.id if hasattr(chunk, 'id') else None,
                "page_number": page_num,
                "section": section_title,
                "document_id": metadata.get('document_id'),
                "type": metadata.get('chunk_type', 'chunk'),
                "fileUrl": file_url,
                "start_time": start_time,
                "end_time": end_time
            })
        
        # Sort by score (highest first)
        sources.sort(key=lambda x: x['score'], reverse=True)
        
        # Strictly limit to 4 sources
        return sources[:4]
    
    def _generate_relevance_summary(self, content: str, section: str) -> str:
        """Generate a one-sentence summary of why this content is relevant"""
        
        # Clean up the content - don't truncate for relevance summary
        content_clean = content.strip()[:500]  # Allow more content for better topic extraction
        
        # If section title is informative, use it
        if section and section != "Main Content":
            key_topic = self._extract_key_topic(content_clean)
            return f"Discusses {section} with insights on {key_topic}"
        
        # Extract key concepts from the content
        key_topic = self._extract_key_topic(content_clean)
        
        # Generate a concise summary based on content patterns
        content_lower = content_clean.lower()
        
        if "definition" in content_lower or "is defined as" in content_lower:
            return f"Defines key concepts related to {key_topic}"
        elif "example" in content_lower or "case" in content_lower:
            return f"Provides examples and case studies about {key_topic}"
        elif "how to" in content_lower or "steps" in content_lower or "process" in content_lower:
            return f"Explains practical approaches for {key_topic}"
        elif "importance" in content_lower or "critical" in content_lower or "essential" in content_lower:
            return f"Highlights the importance of {key_topic}"
        elif "challenge" in content_lower or "problem" in content_lower or "issue" in content_lower:
            return f"Addresses challenges related to {key_topic}"
        elif "benefit" in content_lower or "advantage" in content_lower or "value" in content_lower:
            return f"Outlines benefits and value of {key_topic}"
        elif "strategy" in content_lower or "strategic" in content_lower:
            return f"Presents strategic considerations for {key_topic}"
        elif "best practice" in content_lower or "recommendation" in content_lower:
            return f"Recommends best practices for {key_topic}"
        else:
            return f"Provides insights on {key_topic}"
    
    def _extract_key_topic(self, text: str) -> str:
        """Extract the main topic from a text snippet"""
        
        # Common HR/organizational keywords to look for
        keywords = [
            'leadership', 'culture', 'organization', 'talent', 'performance',
            'strategy', 'capability', 'transformation', 'development', 'engagement',
            'customer', 'innovation', 'change', 'effectiveness', 'management',
            'team', 'collaboration', 'communication', 'skills', 'competency',
            'assessment', 'metrics', 'accountability', 'alignment', 'execution'
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in keywords if kw in text_lower]
        
        if found_keywords:
            # Return the most relevant keyword (first found)
            return found_keywords[0]
        
        # Extract first meaningful noun phrase
        words = text.split()[:10]
        meaningful_words = [w for w in words if len(w) > 4 and w.isalpha()]
        
        if meaningful_words:
            return meaningful_words[0].lower()
        
        return "organizational practices"
    
    def _is_structured_query(self, query: str) -> bool:
        """Detect if query is asking for structured content like lists or steps"""
        structured_keywords = [
            'dimensions', 'steps', 'list', 'factors', 'elements', 'components',
            'aspects', 'ways', 'methods', 'stages', 'phases', 'points',
            'how to build', 'how to create', 'how to develop', 'process',
            'framework', 'model', 'approach', 'strategy', 'plan', 'improve',
            'six steps', 'six-step', 'logic'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in structured_keywords)
    
    async def _get_sequential_chunks(self, documents: List[Dict], index) -> List[Dict]:
        """Get sequential chunks from the same document to capture complete lists"""
        
        try:
            # Group documents by filename and page
            doc_groups = {}
            for doc in documents[:3]:  # Only process top 3 for performance
                key = f"{doc['filename']}_{doc.get('page_number', 'unknown')}"
                if key not in doc_groups:
                    doc_groups[key] = []
                doc_groups[key].append(doc)
            
            enhanced_docs = list(documents)  # Start with original documents
            
            # For each group, try to get sequential chunks
            for group_key, group_docs in doc_groups.items():
                if not group_docs or not group_docs[0].get('chunk_id'):
                    continue
                    
                # Extract the numeric part of chunk_id to find sequential chunks
                base_chunk_id = group_docs[0]['chunk_id']
                logger.info(f"Looking for sequential chunks around: {base_chunk_id}")
                
                # Try to find sequential chunks by modifying the chunk ID
                sequential_ids = []
                if '_' in base_chunk_id:
                    parts = base_chunk_id.split('_')
                    if len(parts) >= 2 and parts[-1].isdigit():
                        base_num = int(parts[-1])
                        filename_part = '_'.join(parts[:-1])
                        
                        # Get a wider range for numbered sequences (like "six steps")
                        # Check if this looks like it might be part of a numbered sequence
                        is_numbered_sequence = any(num in str(doc.get('content', '')).lower() 
                                                 for num in ['4.1', '4.2', '4.3', '4.4', '4.5', '4.6', 
                                                           'step 1', 'step 2', 'step 3', 'step 4', 'step 5', 'step 6'])
                        
                        if is_numbered_sequence:
                            # More aggressive search for numbered sequences
                            for offset in range(-8, 9):  # Much wider range
                                if offset != 0:
                                    seq_id = f"{filename_part}_{base_num + offset}"
                                    sequential_ids.append(seq_id)
                        else:
                            # Normal range for other structured content
                            for offset in [-2, -1, 1, 2, 3]:
                                seq_id = f"{filename_part}_{base_num + offset}"
                                sequential_ids.append(seq_id)
                
                # Fetch sequential chunks
                if sequential_ids:
                    try:
                        fetch_results = index.fetch(sequential_ids)
                        for seq_id, vector_data in fetch_results.vectors.items():
                            if vector_data and hasattr(vector_data, 'metadata'):
                                # Add sequential chunk if it doesn't already exist
                                existing_ids = {doc.get('chunk_id') for doc in enhanced_docs}
                                if seq_id not in existing_ids:
                                    enhanced_docs.append({
                                        'content': vector_data.metadata.get('content', ''),
                                        'title': vector_data.metadata.get('title', ''),
                                        'filename': vector_data.metadata.get('filename', ''),
                                        'page_number': vector_data.metadata.get('page_number', ''),
                                        'score': 0.5,  # Lower score for sequential chunks
                                        'chunk_id': seq_id
                                    })
                                    
                        logger.info(f"Added {len(fetch_results.vectors)} sequential chunks for {group_key}")
                        
                        # Log some content to verify we're getting the right chunks
                        for seq_id, vector_data in list(fetch_results.vectors.items())[:2]:
                            content_preview = vector_data.metadata.get('content', '')[:100] if vector_data else ''
                            logger.info(f"Sequential chunk {seq_id}: {content_preview}...")
                        
                    except Exception as fetch_error:
                        logger.warning(f"Could not fetch sequential chunks: {fetch_error}")
            
            # Sort by score (original matches first, then sequential)
            enhanced_docs.sort(key=lambda x: x['score'], reverse=True)
            
            # Increased limit for numbered sequences
            max_docs = 25 if any('4.1' in str(doc.get('content', '')) or 'step' in str(doc.get('content', '')).lower() 
                               for doc in enhanced_docs) else 15
            
            logger.info(f"Returning {min(len(enhanced_docs), max_docs)} documents (max: {max_docs})")
            return enhanced_docs[:max_docs]
            
        except Exception as e:
            logger.error(f"Error getting sequential chunks: {e}")
            return documents  # Return original if error
    
    def format_sources(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Legacy format_sources method for backward compatibility"""
        return self.format_sources_enhanced(context_data)
    
    async def log_analytics(self, query: str, response: Dict[str, Any], session_id: Optional[str]):
        """Log analytics for the query"""
        
        try:
            if db.engine:
                from sqlalchemy import text
                
                with db.engine.connect() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO analytics_events (event_type, event_data, session_id, created_at)
                            VALUES (:event_type, :event_data, :session_id, :created_at)
                        """),
                        {
                            'event_type': 'chat_query',
                            'event_data': json.dumps({
                                'query': query,
                                'response_length': len(response.get('answer', '')),
                                'num_sources': len(response.get('sources', [])),
                                'has_error': 'error' in response
                            }),
                            'session_id': session_id,
                            'created_at': datetime.now()
                        }
                    )
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Error logging analytics: {e}")

# Create global chat service instance
chat_service = ChatService()