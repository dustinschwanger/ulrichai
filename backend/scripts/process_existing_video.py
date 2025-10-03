"""
Script to manually process existing video that failed or was uploaded before indexing was implemented
"""
import asyncio
import sys
from app.core.database import db
from app.lms.models.lesson_media import LessonMedia
from app.lms.services.video_indexing_service import video_indexing_service

async def process_video(media_id: str):
    """Process a single video by media ID"""
    print(f"Starting processing for video {media_id}...")
    await video_indexing_service.process_lesson_video(media_id)
    print(f"Processing completed for video {media_id}")

async def process_all_pending_videos():
    """Process all videos with pending or error status"""
    session = db.get_session()

    if not session:
        print("ERROR: Could not create database session")
        return

    try:
        # Find videos that need processing
        videos = session.query(LessonMedia).filter(
            LessonMedia.media_type == 'video',
            LessonMedia.transcription_status.in_(['pending', 'error', None])
        ).all()

        print(f"Found {len(videos)} videos to process")

        for video in videos:
            print(f"\nProcessing: {video.title} (ID: {video.id})")
            print(f"  Current status: {video.transcription_status}")
            print(f"  Indexed: {video.is_indexed}")

            await video_indexing_service.process_lesson_video(str(video.id))

    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Process specific video by ID
        media_id = sys.argv[1]
        asyncio.run(process_video(media_id))
    else:
        # Process all pending videos
        asyncio.run(process_all_pending_videos())
