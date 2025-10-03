#!/usr/bin/env python3
"""
Migration script to move existing local videos to Supabase storage.

This script:
1. Finds all lessons with locally-stored videos
2. Uploads videos to Supabase
3. Updates database with new Supabase paths
4. Keeps local files as backup (doesn't delete them)

Usage:
    python migrate_videos_to_supabase.py [--dry-run]
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import db
from app.lms.models import Lesson
from app.lms.services.storage_service import storage_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def migrate_lesson_videos(dry_run=False):
    """Migrate all locally-stored videos to Supabase"""

    if not storage_service.is_available():
        logger.error("Supabase storage is not available. Check your .env configuration.")
        return False

    session = db.get_session()
    if not session:
        logger.error("Could not get database session")
        return False

    try:
        # Find all lessons with media files
        lessons = session.query(Lesson).filter(
            Lesson.content_data.isnot(None)
        ).all()

        logger.info(f"Found {len(lessons)} lessons to check")

        migrated_count = 0
        error_count = 0
        skipped_count = 0

        for lesson in lessons:
            if not lesson.content_data:
                continue

            # Check primary_video
            primary_video = lesson.content_data.get("primary_video")
            media_files = lesson.content_data.get("media_files", [])

            # Collect videos to migrate
            videos_to_migrate = []

            if primary_video and primary_video.get("storage") == "local":
                videos_to_migrate.append(("primary_video", primary_video))

            for i, media in enumerate(media_files):
                if media.get("type") == "video" and media.get("storage") == "local":
                    videos_to_migrate.append((f"media_files[{i}]", media))

            if not videos_to_migrate:
                skipped_count += 1
                continue

            logger.info(f"\n{'='*80}")
            logger.info(f"Lesson: {lesson.title} (ID: {lesson.id})")
            logger.info(f"Videos to migrate: {len(videos_to_migrate)}")

            for location, video in videos_to_migrate:
                try:
                    # Get local file path
                    local_path = Path("uploads") / video.get("path", "")

                    if not local_path.exists():
                        logger.error(f"  ❌ Local file not found: {local_path}")
                        error_count += 1
                        continue

                    file_size_mb = local_path.stat().st_size / (1024 * 1024)
                    logger.info(f"  📹 {video.get('filename')} ({file_size_mb:.2f} MB)")
                    logger.info(f"     Location: {location}")
                    logger.info(f"     Path: {local_path}")

                    if dry_run:
                        logger.info(f"     [DRY RUN] Would upload to Supabase")
                        continue

                    # Read file content
                    with local_path.open("rb") as f:
                        file_content = f.read()

                    # Determine content type
                    content_type_map = {
                        ".mp4": "video/mp4",
                        ".webm": "video/webm",
                        ".mov": "video/quicktime",
                        ".avi": "video/x-msvideo",
                        ".mkv": "video/x-matroska",
                    }
                    file_extension = local_path.suffix.lower()
                    content_type = content_type_map.get(file_extension, "video/mp4")

                    # Upload to Supabase
                    logger.info(f"     ⬆️  Uploading to Supabase...")

                    result = await storage_service.upload_file(
                        file_content=file_content,
                        filename=local_path.name,
                        bucket="lms-videos",
                        path=f"lessons/{lesson.id}",
                        content_type=content_type
                    )

                    # Update video metadata
                    video["bucket"] = "lms-videos"
                    video["path"] = result["path"]
                    video["storage"] = "supabase"
                    video["migrated_at"] = datetime.now(timezone.utc).isoformat()
                    video["old_local_path"] = str(local_path)

                    # Remove old 'url' field if it exists
                    if "url" in video:
                        del video["url"]

                    logger.info(f"     ✅ Uploaded to Supabase: {result['path']}")

                    migrated_count += 1

                except Exception as e:
                    logger.error(f"     ❌ Failed to migrate {video.get('filename')}: {e}")
                    error_count += 1

        # Commit all changes if not dry run
        if not dry_run:
            session.commit()
            logger.info(f"\n{'='*80}")
            logger.info("✅ Database updated with new Supabase paths")

        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("MIGRATION SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Lessons checked:    {len(lessons)}")
        logger.info(f"Videos migrated:    {migrated_count}")
        logger.info(f"Errors:             {error_count}")
        logger.info(f"Skipped (no local): {skipped_count}")

        if dry_run:
            logger.info("\n⚠️  DRY RUN - No changes were made")
        else:
            logger.info("\n✅ Migration complete!")
            logger.info("\nNote: Local video files were NOT deleted.")
            logger.info("They remain in the uploads/ directory as backup.")

        return error_count == 0

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate local videos to Supabase storage")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes"
    )

    args = parser.parse_args()

    logger.info("="*80)
    logger.info("VIDEO MIGRATION TO SUPABASE")
    logger.info("="*80)

    if args.dry_run:
        logger.info("Running in DRY RUN mode - no changes will be made\n")

    # Run the migration
    success = asyncio.run(migrate_lesson_videos(dry_run=args.dry_run))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()