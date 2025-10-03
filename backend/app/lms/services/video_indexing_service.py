"""
Video Indexing Service - Transcribes lesson videos and indexes them to Pinecone for AI chat
"""
import logging
import json
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
import openai
import os

from ...processing.video_processor import VideoProcessor
from ...processing.video_chunker import VideoChunker
from ...core.vector_store import vector_store
from ...lms.services.storage_service import storage_service
from ...lms.models.lesson_media import LessonMedia
from ...lms.models.content import Lesson, Module
from ...lms.models.course import CourseVersion, Course
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class VideoIndexingService:
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.video_chunker = VideoChunker({
            'chunkSize': 1000,
            'chunkOverlap': 200,
            'minSegmentDuration': 10.0,
            'maxSegmentDuration': 120.0
        })

    async def process_lesson_video(self, media_id: str):
        """
        Process a lesson video: download, transcribe, chunk, and index to Pinecone
        """
        # Create own DB session for background task
        from ...core.database import db as database
        db = database.get_session()

        if not db:
            logger.error("Could not create database session for video processing")
            return

        try:
            # Get media record
            media = db.query(LessonMedia).filter(LessonMedia.id == UUID(media_id)).first()

            if not media:
                logger.error(f"Media {media_id} not found")
                return

            if media.media_type != 'video':
                logger.info(f"Media {media_id} is not a video, skipping")
                return

            # Update status to processing
            media.transcription_status = 'processing'
            db.commit()

            logger.info(f"Starting video processing for media {media_id}")

            # Download video from Supabase
            if media.storage != 'supabase':
                logger.error(f"Media {media_id} is not in Supabase storage")
                media.transcription_status = 'error'
                db.commit()
                return

            video_content = await storage_service.download_file(
                bucket=media.bucket,
                file_path=media.path
            )

            if not video_content:
                logger.error(f"Failed to download video {media_id}")
                media.transcription_status = 'error'
                db.commit()
                return

            # Transcribe video
            logger.info(f"Transcribing video {media_id}")
            transcript_result = await self.video_processor.process_video(
                video_content=video_content,
                filename=media.filename
            )

            # Store transcript data
            media.transcription_data = json.dumps(transcript_result['transcript'])
            media.transcription_status = 'completed'
            db.commit()

            logger.info(f"Transcription completed for {media_id}")

            # Get lesson and course context
            lesson = db.query(Lesson).filter(Lesson.id == media.lesson_id).first()
            if not lesson:
                logger.error(f"Lesson not found for media {media_id}")
                return

            module = db.query(Module).filter(Module.id == lesson.module_id).first()
            if not module:
                logger.error(f"Module not found for lesson {lesson.id}")
                return

            course_version = db.query(CourseVersion).filter(CourseVersion.id == module.course_version_id).first()
            if not course_version:
                logger.error(f"CourseVersion not found for module {module.id}")
                return

            course = db.query(Course).filter(Course.id == course_version.course_id).first()
            if not course:
                logger.error(f"Course not found for course_version {course_version.id}")
                return

            # Chunk the transcript
            metadata = {
                'filename': media.filename,
                'display_name': media.display_name or media.title,
                'document_source': media.document_source or 'Course Content',
                'document_type': media.document_type or 'Video',
                'capability_domain': media.capability_domain,
                'author': media.author,
                'lesson_id': str(lesson.id),
                'lesson_title': lesson.title,
                'module_id': str(module.id),
                'module_title': module.title,
                'course_id': str(course.id),
                'course_title': course.title,
            }

            chunks = self.video_chunker.chunk_video_transcript(
                transcript_data=transcript_result['transcript'],
                metadata=metadata
            )

            logger.info(f"Created {len(chunks)} chunks for video {media_id}")

            # Index chunks to Pinecone
            chunks_indexed = 0
            for i, chunk in enumerate(chunks):
                try:
                    chunk_id = f"lesson_{media.lesson_id}_media_{media_id}_chunk_{i}"

                    # Generate embedding
                    embedding_response = openai.embeddings.create(
                        model="text-embedding-3-large",
                        input=chunk.content,
                        dimensions=1024
                    )
                    embedding = embedding_response.data[0].embedding

                    # Prepare metadata for Pinecone
                    pinecone_metadata = {
                        'content': chunk.content,
                        'media_id': media_id,
                        'lesson_id': str(lesson.id),
                        'lesson_title': lesson.title,
                        'module_id': str(module.id),
                        'module_title': module.title,
                        'course_id': str(course.id),
                        'course_title': course.title,
                        'filename': media.filename,
                        'title': media.display_name or media.title,
                        'display_name': media.display_name or media.title,
                        'section': media.document_source or course.title,
                        'content_type': 'lesson_video',
                        'document_type': media.document_type or 'Video',
                        'capability_domain': metadata.get('capability_domain', ''),
                        'author': metadata.get('author', ''),
                        'start_time': chunk.start_time,
                        'end_time': chunk.end_time,
                        'duration': chunk.end_time - chunk.start_time,
                        'timestamp_display': chunk.metadata.get('timestamp_display', ''),
                        'language': chunk.metadata.get('language', 'en')
                    }

                    # Store in Pinecone
                    vector_store.index.upsert(
                        vectors=[(chunk_id, embedding, pinecone_metadata)]
                    )

                    chunks_indexed += 1

                except Exception as e:
                    logger.error(f"Error indexing chunk {i} for media {media_id}: {e}")
                    continue

            # Update indexed status
            media.is_indexed = 'yes'
            media.indexed_at = datetime.now(timezone.utc)
            db.commit()

            logger.info(f"Successfully indexed {chunks_indexed}/{len(chunks)} chunks for video {media_id}")

        except Exception as e:
            logger.error(f"Error processing video {media_id}: {e}", exc_info=True)
            # Update status to error
            try:
                media = db.query(LessonMedia).filter(LessonMedia.id == UUID(media_id)).first()
                if media:
                    media.transcription_status = 'error'
                    media.is_indexed = 'error'
                    db.commit()
            except:
                pass
        finally:
            # Close DB session
            if db:
                db.close()

# Singleton instance
video_indexing_service = VideoIndexingService()
