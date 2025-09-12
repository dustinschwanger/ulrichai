import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pypdf import PdfReader
from docx import Document as DocxDocument
from pptx import Presentation
import logging
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import re

load_dotenv()

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.anthropic = Anthropic(api_key=api_key)
        else:
            self.anthropic = None
            print("WARNING: ANTHROPIC_API_KEY not set, AI features will be disabled")
        self.chunk_size = 500  # tokens
        self.chunk_overlap = 100  # tokens
        
    async def process_document(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Process document and extract hierarchical structure"""
        
        # Extract text based on file type - NOW WITH PAGE TRACKING
        if file_type == 'pdf':
            text, page_map = await self.extract_pdf_text_with_pages(file_path)
        elif file_type in ['docx', 'doc']:
            text = await self.extract_docx_text(file_path)
            page_map = None  # Word docs don't have fixed pages
        elif file_type in ['pptx', 'ppt']:
            text, page_map = await self.extract_pptx_text_with_slides(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Generate document ID
        doc_id = hashlib.md5(text.encode()).hexdigest()
        
        # Generate document summary
        summary = await self.generate_summary(text)
        
        # Extract key concepts
        concepts = await self.extract_concepts(text)
        
        # Identify sections
        sections = await self.identify_sections(text)
        
        # Create chunks with overlap AND PAGE NUMBERS
        chunks = await self.create_smart_chunks(text, sections, page_map)
        
        return {
            'doc_id': doc_id,
            'text': text,
            'summary': summary,
            'concepts': concepts,
            'sections': sections,
            'chunks': chunks,
            'file_type': file_type,
            'file_path': file_path
        }
    
    async def extract_pdf_text_with_pages(self, file_path: str) -> Tuple[str, List[Dict]]:
        """Extract text from PDF with page number tracking"""
        try:
            reader = PdfReader(file_path)
            full_text = ""
            page_map = []  # Track where each page starts/ends in the text
            
            current_position = 0
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    start_pos = current_position
                    end_pos = current_position + len(page_text)
                    
                    page_map.append({
                        'page_number': page_num,
                        'start_char': start_pos,
                        'end_char': end_pos,
                        'text': page_text
                    })
                    
                    full_text += page_text + "\n"
                    current_position = end_pos + 1  # +1 for the newline
            
            return full_text, page_map
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise
    
    async def extract_pptx_text_with_slides(self, file_path: str) -> Tuple[str, List[Dict]]:
        """Extract text from PowerPoint with slide number tracking"""
        try:
            prs = Presentation(file_path)
            full_text = ""
            page_map = []  # Treat slides as pages
            
            current_position = 0
            for slide_num, slide in enumerate(prs.slides, start=1):
                slide_text = ""
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        slide_text += shape.text + "\n"
                
                if slide_text:
                    start_pos = current_position
                    end_pos = current_position + len(slide_text)
                    
                    page_map.append({
                        'page_number': slide_num,
                        'start_char': start_pos,
                        'end_char': end_pos,
                        'text': slide_text
                    })
                    
                    full_text += slide_text
                    current_position = end_pos
            
            return full_text, page_map
        except Exception as e:
            logger.error(f"Error extracting PPTX text: {e}")
            raise
    
    async def extract_docx_text(self, file_path: str) -> str:
        """Extract text from Word document"""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            raise
    
    def find_page_for_position(self, char_position: int, page_map: List[Dict]) -> Optional[int]:
        """Find which page a character position belongs to"""
        if not page_map:
            return None
            
        for page_info in page_map:
            if page_info['start_char'] <= char_position <= page_info['end_char']:
                return page_info['page_number']
        
        # If position is beyond last page, return last page number
        if page_map and char_position > page_map[-1]['end_char']:
            return page_map[-1]['page_number']
        
        return None
    
    async def create_smart_chunks(self, text: str, sections: List[Dict], page_map: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
        """Create overlapping chunks with section awareness AND PAGE NUMBERS"""
        chunks = []
        chunk_id = 0
        
        for section in sections:
            section_text = section['text']
            section_start_char = text.find(section_text)  # Find where this section starts in full text
            words = section_text.split()
            
            # Approximate tokens (rough estimate: 1 token ≈ 0.75 words)
            words_per_chunk = int(self.chunk_size * 0.75)
            overlap_words = int(self.chunk_overlap * 0.75)
            
            start = 0
            while start < len(words):
                end = min(start + words_per_chunk, len(words))
                chunk_text = ' '.join(words[start:end])
                
                # Find the character position of this chunk in the full text
                chunk_start_in_section = len(' '.join(words[:start]))
                chunk_char_position = section_start_char + chunk_start_in_section if section_start_char >= 0 else 0
                
                # Find which page this chunk belongs to
                page_number = self.find_page_for_position(chunk_char_position, page_map) if page_map else None
                
                chunks.append({
                    'chunk_id': f"chunk_{chunk_id}",
                    'section_title': section['title'],
                    'text': chunk_text,
                    'start_word': start,
                    'end_word': end,
                    'page_number': page_number  # ADD PAGE NUMBER TO EACH CHUNK
                })
                
                chunk_id += 1
                start += words_per_chunk - overlap_words
                
                if start >= len(words):
                    break
        
        return chunks
    
    async def generate_summary(self, text: str) -> str:
        """Generate document summary using Claude"""
        try:
            # Limit text length for summary
            max_chars = 10000
            truncated_text = text[:max_chars] if len(text) > max_chars else text
            
            response = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"""Provide a comprehensive summary of this document in 2-3 paragraphs. 
                    Focus on the main topics, key concepts, and practical applications.
                    
                    Document text:
                    {truncated_text}"""
                }]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Summary generation failed"
    
    async def extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from document"""
        try:
            # Simple keyword extraction for now
            # Could enhance with Claude or NLP libraries
            concepts = []
            
            # Look for capitalized phrases (likely important terms)
            pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            matches = re.findall(pattern, text)
            
            # Get unique concepts
            seen = set()
            for match in matches:
                if len(match) > 3 and match not in seen:
                    concepts.append(match)
                    seen.add(match)
                    if len(concepts) >= 20:
                        break
            
            return concepts
        except Exception as e:
            logger.error(f"Error extracting concepts: {e}")
            return []
    
    async def identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify document sections"""
        sections = []
        
        # Look for headers (simple approach)
        lines = text.split('\n')
        current_section = ""
        section_start = 0
        
        for i, line in enumerate(lines):
            # Simple heuristic: short lines in caps or with numbers
            if len(line) < 100 and (line.isupper() or re.match(r'^\d+\.', line)):
                if current_section:
                    sections.append({
                        'title': current_section,
                        'start': section_start,
                        'end': i,
                        'text': '\n'.join(lines[section_start:i])
                    })
                current_section = line.strip()
                section_start = i
        
        # Add last section
        if current_section:
            sections.append({
                'title': current_section,
                'start': section_start,
                'end': len(lines),
                'text': '\n'.join(lines[section_start:])
            })
        
        # If no sections found, treat whole document as one section
        if not sections:
            sections.append({
                'title': 'Full Document',
                'start': 0,
                'end': len(lines),
                'text': text
            })
        
        return sections

# Create processor instance
processor = DocumentProcessor()