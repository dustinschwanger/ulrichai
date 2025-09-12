# backend/app/processing/video_chunker.py

from typing import List, Dict, Any
from dataclasses import dataclass
import logging
import math

logger = logging.getLogger(__name__)

@dataclass
class VideoChunk:
    content: str
    metadata: Dict[str, Any]
    start_time: float
    end_time: float
    segment_ids: List[int]
    chunk_type: str = "video"

class VideoChunker:
    def __init__(self, config: Dict[str, Any]):
        self.chunk_size = config.get('chunkSize', 1000)
        self.chunk_overlap = config.get('chunkOverlap', 200)
        self.min_segment_duration = config.get('minSegmentDuration', 10.0)  # 10 seconds minimum
        self.max_segment_duration = config.get('maxSegmentDuration', 120.0)  # 2 minutes maximum
        
    def chunk_video_transcript(self, transcript_data: Dict[str, Any], metadata: Dict[str, Any]) -> List[VideoChunk]:
        """
        Chunk video transcript preserving temporal coherence and timestamp information.
        """
        chunks = []
        
        segments = transcript_data.get('segments', [])
        if not segments:
            logger.warning("No transcript segments found")
            return []
        
        logger.info(f"Chunking {len(segments)} transcript segments")
        
        # Group segments into coherent chunks
        segment_groups = self._group_segments_by_content(segments)
        
        for group in segment_groups:
            chunk = self._create_chunk_from_segments(group, metadata, transcript_data)
            chunks.append(chunk)
            
        logger.info(f"Created {len(chunks)} video chunks")
        return chunks
    
    def _group_segments_by_content(self, segments: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Group segments into coherent chunks based on content length and temporal boundaries.
        """
        groups = []
        current_group = []
        current_length = 0
        
        for segment in segments:
            segment_text = segment.get('text', '').strip()
            segment_length = len(segment_text)
            
            # Check if we should start a new group
            should_start_new = (
                # Content-based: Current group is getting too long
                (current_length + segment_length > self.chunk_size and current_group) or
                
                # Time-based: Current group duration is too long
                (current_group and 
                 segment.get('start', 0) - current_group[0].get('start', 0) > self.max_segment_duration) or
                 
                # Logical break detection: Long pause or significant topic change
                self._detect_logical_break(current_group, segment)
            )
            
            if should_start_new and current_group:
                # Ensure minimum duration unless it's the last possible group
                if (current_group[-1].get('end', 0) - current_group[0].get('start', 0) >= self.min_segment_duration or
                    not current_group):
                    groups.append(current_group)
                    current_group = []
                    current_length = 0
            
            # Add segment to current group
            current_group.append(segment)
            current_length += segment_length
        
        # Add the last group
        if current_group:
            groups.append(current_group)
        
        # Post-process: merge very short groups with adjacent ones
        groups = self._merge_short_groups(groups)
        
        return groups
    
    def _detect_logical_break(self, current_group: List[Dict[str, Any]], next_segment: Dict[str, Any]) -> bool:
        """
        Detect logical breaks in content that suggest a new chunk should start.
        """
        if not current_group:
            return False
            
        last_segment = current_group[-1]
        
        # Time-based break: significant pause (more than 3 seconds)
        time_gap = next_segment.get('start', 0) - last_segment.get('end', 0)
        if time_gap > 3.0:
            return True
        
        # Content-based break: look for transition indicators
        next_text = next_segment.get('text', '').strip().lower()
        transition_indicators = [
            'now', 'next', 'moving on', 'let\'s talk about', 'another',
            'in conclusion', 'to summarize', 'finally', 'lastly',
            'first', 'second', 'third', 'meanwhile', 'however', 'but'
        ]
        
        if any(indicator in next_text[:50] for indicator in transition_indicators):
            return True
            
        return False
    
    def _merge_short_groups(self, groups: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
        """
        Merge groups that are too short with adjacent groups.
        """
        if len(groups) <= 1:
            return groups
            
        merged_groups = []
        i = 0
        
        while i < len(groups):
            current_group = groups[i]
            current_duration = self._get_group_duration(current_group)
            current_text_length = sum(len(seg.get('text', '')) for seg in current_group)
            
            # Check if this group is too short
            if (current_duration < self.min_segment_duration or current_text_length < self.chunk_size // 3) and len(groups) > 1:
                # Try to merge with next group
                if i + 1 < len(groups):
                    next_group = groups[i + 1]
                    merged_group = current_group + next_group
                    merged_duration = self._get_group_duration(merged_group)
                    
                    # Only merge if the result isn't too long
                    if merged_duration <= self.max_segment_duration:
                        merged_groups.append(merged_group)
                        i += 2  # Skip the next group since we merged it
                        continue
                
                # Try to merge with previous group
                if merged_groups:
                    last_group = merged_groups[-1]
                    merged_group = last_group + current_group
                    merged_duration = self._get_group_duration(merged_group)
                    
                    if merged_duration <= self.max_segment_duration:
                        merged_groups[-1] = merged_group
                        i += 1
                        continue
            
            # Keep the group as is
            merged_groups.append(current_group)
            i += 1
            
        return merged_groups
    
    def _get_group_duration(self, group: List[Dict[str, Any]]) -> float:
        """Get the duration of a segment group."""
        if not group:
            return 0.0
        return group[-1].get('end', 0) - group[0].get('start', 0)
    
    def _create_chunk_from_segments(self, segments: List[Dict[str, Any]], 
                                   base_metadata: Dict[str, Any], 
                                   transcript_data: Dict[str, Any]) -> VideoChunk:
        """
        Create a VideoChunk from a group of segments.
        """
        if not segments:
            raise ValueError("Cannot create chunk from empty segments")
        
        # Combine text from all segments
        combined_text = ' '.join(segment.get('text', '').strip() for segment in segments)
        
        # Get timing information
        start_time = segments[0].get('start', 0.0)
        end_time = segments[-1].get('end', 0.0)
        segment_ids = [segment.get('id', i) for i, segment in enumerate(segments)]
        
        # Create enhanced metadata
        chunk_metadata = {
            **base_metadata,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'segment_count': len(segments),
            'language': transcript_data.get('language', 'en'),
            'avg_confidence': self._calculate_avg_confidence(segments),
            'content_type': 'video_transcript'
        }
        
        # Add readable timestamp for display
        chunk_metadata['timestamp_display'] = self._format_timestamp(start_time)
        chunk_metadata['duration_display'] = self._format_duration(end_time - start_time)
        
        return VideoChunk(
            content=combined_text,
            metadata=chunk_metadata,
            start_time=start_time,
            end_time=end_time,
            segment_ids=segment_ids,
            chunk_type="video"
        )
    
    def _calculate_avg_confidence(self, segments: List[Dict[str, Any]]) -> float:
        """Calculate average confidence score for segments."""
        confidences = []
        for segment in segments:
            # Use negative log probability as confidence indicator
            avg_logprob = segment.get('avg_logprob', -1.0)
            if avg_logprob != 0:
                confidence = math.exp(avg_logprob) if avg_logprob > -10 else 0.0
                confidences.append(confidence)
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp as MM:SS or HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.0f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"