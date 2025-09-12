# backend/app/processing/smart_chunker.py

import re
from typing import List, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    content: str
    metadata: Dict[str, Any]
    start_page: int = None
    end_page: int = None
    section: str = None
    chunk_type: str = "text"  # text, table, list, heading

class SmartChunker:
    def __init__(self, config: Dict[str, Any]):
        self.chunk_size = config.get('chunkSize', 1000)
        self.chunk_overlap = config.get('chunkOverlap', 200)
        self.keep_tables_intact = config.get('keepTablesIntact', True)
        self.keep_lists_intact = config.get('keepListsIntact', True)
        self.section_headers = config.get('sectionHeaders', ['Chapter', 'Section', 'Part'])
        
    def chunk_document(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Intelligently chunk a document based on structure and configuration.
        """
        chunks = []
        
        # Split by sections first
        sections = self._split_by_sections(text)
        
        for section in sections:
            section_chunks = self._chunk_section(
                section['content'],
                section['title'],
                metadata
            )
            chunks.extend(section_chunks)
        
        return chunks
    
    def _split_by_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Split document by section headers.
        """
        sections = []
        
        # If no headers defined or text is short, treat entire doc as one section
        if not self.section_headers or len(text) < self.chunk_size * 2:
            return [{'title': 'Main Content', 'content': text}]
        
        # Create regex pattern for section headers
        header_patterns = []
        for header in self.section_headers:
            # Match variations like "Chapter 1", "CHAPTER 1:", "Chapter: Title", etc.
            header_patterns.append(rf'(?:^|\n)({header}[^\n]*)')
            header_patterns.append(rf'(?:^|\n)(\d+\.?\s*{header}[^\n]*)')
            header_patterns.append(rf'(?:^|\n)([A-Z]\.?\s*{header}[^\n]*)')
        
        header_pattern = '|'.join(header_patterns)
        
        # Split by headers
        parts = re.split(f'({header_pattern})', text, flags=re.IGNORECASE | re.MULTILINE)
        
        current_section = {'title': 'Introduction', 'content': ''}
        
        for i, part in enumerate(parts):
            if part is None:
                continue
                
            part = part.strip()
            if not part:
                continue
                
            # Check if this part is a header
            is_header = False
            if i > 0:  # Don't check the first part
                for header in self.section_headers:
                    if header.lower() in part.lower():
                        is_header = True
                        break
            
            if is_header:
                # Save previous section if it has content
                if current_section['content'].strip():
                    sections.append(current_section)
                # Start new section
                current_section = {'title': part, 'content': ''}
            else:
                # Add to current section content
                current_section['content'] += '\n' + part if current_section['content'] else part
        
        # Add the last section
        if current_section['content'].strip():
            sections.append(current_section)
        
        # If no sections were created, return the whole text as one section
        if not sections:
            sections = [{'title': 'Main Content', 'content': text}]
        
        return sections
    
    def _chunk_section(self, text: str, section_title: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Chunk a section while preserving structure.
        """
        chunks = []
        
        # Identify special content blocks
        blocks = self._identify_content_blocks(text)
        
        current_chunk = ""
        current_metadata = {
            **metadata,
            'section': section_title
        }
        
        for block in blocks:
            if block['type'] in ['table', 'list'] and self._should_keep_intact(block['type']):
                # Add current chunk if it exists
                if current_chunk.strip():
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        metadata=current_metadata,
                        section=section_title,
                        chunk_type='text'
                    ))
                    current_chunk = ""
                
                # Add special block as its own chunk
                chunks.append(Chunk(
                    content=block['content'],
                    metadata={**current_metadata, 'block_type': block['type']},
                    section=section_title,
                    chunk_type=block['type']
                ))
            else:
                # Regular text - apply size-based chunking
                sentences = self._split_into_sentences(block['content'])
                
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > self.chunk_size:
                        if current_chunk.strip():
                            chunks.append(Chunk(
                                content=current_chunk.strip(),
                                metadata=current_metadata,
                                section=section_title,
                                chunk_type='text'
                            ))
                        # Start new chunk with overlap if configured
                        if self.chunk_overlap > 0 and current_chunk:
                            overlap = self._get_overlap(current_chunk)
                            current_chunk = overlap + " " + sentence
                        else:
                            current_chunk = sentence
                    else:
                        current_chunk += " " + sentence if current_chunk else sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                metadata=current_metadata,
                section=section_title,
                chunk_type='text'
            ))
        
        return chunks
    
    def _identify_content_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        Identify tables, lists, and other structured content.
        """
        blocks = []
        
        # Simple pattern matching for lists (bullet points or numbered)
        list_pattern = r'(?:^|\n)((?:[\*\-•]\s+[^\n]+\n?)+|(?:\d+[\.\)]\s+[^\n]+\n?)+)'
        
        # Simple pattern for tables (lines with multiple | separators)
        table_pattern = r'(?:^|\n)((?:[^\n]*\|[^\n]*\n)+)'
        
        # Combined pattern
        combined_pattern = f'({table_pattern})|({list_pattern})'
        
        last_end = 0
        
        for match in re.finditer(combined_pattern, text, re.MULTILINE):
            # Add text before this block
            if match.start() > last_end:
                text_before = text[last_end:match.start()].strip()
                if text_before:
                    blocks.append({
                        'type': 'text',
                        'content': text_before
                    })
            
            # Determine block type and add it
            if match.group(1):  # Table
                blocks.append({
                    'type': 'table',
                    'content': match.group(0).strip()
                })
            elif match.group(3):  # List
                blocks.append({
                    'type': 'list',
                    'content': match.group(0).strip()
                })
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(text):
            remaining = text[last_end:].strip()
            if remaining:
                blocks.append({
                    'type': 'text',
                    'content': remaining
                })
        
        # If no special blocks found, return the whole text
        if not blocks:
            blocks = [{'type': 'text', 'content': text}]
        
        return blocks
    
    def _should_keep_intact(self, block_type: str) -> bool:
        """
        Check if a block type should be kept intact.
        """
        if block_type == 'table' and self.keep_tables_intact:
            return True
        if block_type == 'list' and self.keep_lists_intact:
            return True
        return False
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        """
        # Simple sentence splitter - split on period, exclamation, or question mark followed by space
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap(self, chunk: str) -> str:
        """
        Get the overlap portion from the end of a chunk.
        """
        if len(chunk) <= self.chunk_overlap:
            return chunk
        return chunk[-self.chunk_overlap:]