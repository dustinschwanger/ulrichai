# backend/app/processing/video_processor.py

import os
import logging
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path
import openai
from moviepy.editor import VideoFileClip
import ffmpeg

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.max_duration = 3600  # 1 hour max for transcription
        self.audio_format = 'mp3'
        
    async def process_video(self, video_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process video file to extract transcript with timestamps.
        Returns transcript data with timing information.
        """
        try:
            logger.info(f"Starting video processing for: {filename}")
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
                temp_video.write(video_content)
                temp_video_path = temp_video.name
                
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
            
            try:
                # Extract video metadata
                video_info = await self._get_video_info(temp_video_path)
                
                # Check duration limit
                if video_info['duration'] > self.max_duration:
                    raise ValueError(f"Video duration ({video_info['duration']}s) exceeds maximum allowed ({self.max_duration}s)")
                
                # Extract audio from video
                await self._extract_audio(temp_video_path, temp_audio_path)
                
                # Transcribe audio with timestamps
                transcript_data = await self._transcribe_audio(temp_audio_path)
                
                # Combine video info with transcript
                result = {
                    'video_info': video_info,
                    'transcript': transcript_data,
                    'filename': filename
                }
                
                logger.info(f"Successfully processed video: {filename}")
                return result
                
            finally:
                # Clean up temporary files
                for temp_path in [temp_video_path, temp_audio_path]:
                    try:
                        os.unlink(temp_path)
                    except Exception as e:
                        logger.warning(f"Could not delete temp file {temp_path}: {e}")
                        
        except Exception as e:
            logger.error(f"Error processing video {filename}: {e}")
            raise
    
    async def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Extract basic video information using ffmpeg"""
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            if not video_stream:
                raise ValueError("No video stream found")
                
            duration = float(probe['format']['duration'])
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            
            return {
                'duration': duration,
                'width': width,
                'height': height,
                'has_audio': audio_stream is not None,
                'format': probe['format']['format_name'],
                'size_bytes': int(probe['format']['size'])
            }
            
        except Exception as e:
            logger.error(f"Error extracting video info: {e}")
            raise
    
    async def _extract_audio(self, video_path: str, audio_path: str):
        """Extract audio from video using ffmpeg"""
        try:
            logger.info("Extracting audio from video...")
            
            (
                ffmpeg
                .input(video_path)
                .output(audio_path, acodec='mp3', ac=1, ar='16000')  # Mono, 16kHz for Whisper
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info("Audio extraction completed")
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise
    
    async def _transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper API"""
        try:
            logger.info("Starting audio transcription...")
            
            with open(audio_path, 'rb') as audio_file:
                # Use Whisper API with timestamp information
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
                
            # Handle both dict and object responses from OpenAI API
            # Extract basic transcript info
            if isinstance(transcript, dict):
                text = transcript.get('text', '')
                language = transcript.get('language', 'en')
                duration = transcript.get('duration', 0.0)
                segments_data = transcript.get('segments', [])
            else:
                text = getattr(transcript, 'text', '')
                language = getattr(transcript, 'language', 'en')
                duration = getattr(transcript, 'duration', 0.0)
                segments_data = getattr(transcript, 'segments', [])
            
            transcript_data = {
                'text': text,
                'language': language,
                'duration': duration,
                'segments': []
            }
            
            # Process segments - handle both dict and object formats
            for segment in segments_data:
                if isinstance(segment, dict):
                    # Segment is a dictionary
                    segment_info = {
                        'id': segment.get('id', 0),
                        'start': segment.get('start', 0.0),
                        'end': segment.get('end', 0.0),
                        'text': segment.get('text', '').strip(),
                        'tokens': segment.get('tokens', []),
                        'temperature': segment.get('temperature', 0.0),
                        'avg_logprob': segment.get('avg_logprob', 0.0),
                        'compression_ratio': segment.get('compression_ratio', 0.0),
                        'no_speech_prob': segment.get('no_speech_prob', 0.0)
                    }
                else:
                    # Segment is an object
                    segment_info = {
                        'id': getattr(segment, 'id', 0),
                        'start': getattr(segment, 'start', 0.0),
                        'end': getattr(segment, 'end', 0.0),
                        'text': getattr(segment, 'text', '').strip(),
                        'tokens': getattr(segment, 'tokens', []),
                        'temperature': getattr(segment, 'temperature', 0.0),
                        'avg_logprob': getattr(segment, 'avg_logprob', 0.0),
                        'compression_ratio': getattr(segment, 'compression_ratio', 0.0),
                        'no_speech_prob': getattr(segment, 'no_speech_prob', 0.0)
                    }
                
                transcript_data['segments'].append(segment_info)
            
            logger.info(f"Transcription completed: {len(transcript_data['segments'])} segments")
            return transcript_data
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported video formats"""
        return ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv']
    
    def is_video_file(self, filename: str) -> bool:
        """Check if file is a supported video format"""
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.get_supported_formats()