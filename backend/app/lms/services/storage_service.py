import os
import logging
import httpx
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timezone
from uuid import uuid4
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class StorageService:

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        self.chunk_size = 10 * 1024 * 1024
        self.supabase_client: Optional[Client] = None

        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not configured. Storage will fall back to local filesystem.")
        else:
            try:
                self.supabase_client = create_client(self.supabase_url, self.supabase_key)
                if os.getenv("SUPABASE_SERVICE_KEY"):
                    logger.info("Using Supabase service role key for storage uploads")
                else:
                    logger.warning("Using anon key for storage - uploads may fail. Set SUPABASE_SERVICE_KEY for proper permissions.")
            except Exception as e:
                logger.error(f"Failed to create Supabase client: {e}")

    def is_available(self) -> bool:
        return bool(self.supabase_url and self.supabase_key and self.supabase_client)

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        bucket: str,
        path: str,
        content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        if not self.is_available():
            raise Exception("Supabase storage not available")

        file_size = len(file_content)
        file_path = f"{path}/{filename}"

        logger.info(f"Uploading {filename} ({file_size / (1024*1024):.2f} MB) to {bucket}/{file_path}")

        try:
            if file_size <= 50 * 1024 * 1024:
                result = await self._upload_small_file(
                    file_content, bucket, file_path, content_type
                )
            else:
                result = await self._upload_large_file(
                    file_content, bucket, file_path, content_type
                )

            public_url = self.supabase_client.storage.from_(bucket).get_public_url(file_path)

            return {
                "success": True,
                "bucket": bucket,
                "path": file_path,
                "public_url": public_url,
                "size": file_size,
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to upload {filename} to Supabase: {e}")
            raise Exception(f"Storage upload failed: {str(e)}")

    async def _upload_small_file(
        self,
        file_content: bytes,
        bucket: str,
        file_path: str,
        content_type: str
    ) -> Any:
        try:
            result = self.supabase_client.storage.from_(bucket).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "x-upsert": "true"
                }
            )
            logger.info(f"Small file upload successful: {file_path}")
            return result
        except Exception as e:
            logger.error(f"Small file upload failed: {e}")
            raise

    async def _upload_large_file(
        self,
        file_content: bytes,
        bucket: str,
        file_path: str,
        content_type: str
    ) -> Any:
        logger.info(f"Using chunked upload for large file: {file_path}")

        upload_url = f"{self.supabase_url}/storage/v1/object/{bucket}/{file_path}"

        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key,
            "Content-Type": content_type,
            "x-upsert": "true"
        }

        timeout_config = httpx.Timeout(300.0, connect=60.0)

        async with httpx.AsyncClient(timeout=timeout_config) as client:
            logger.info(f"Starting direct upload to Supabase storage...")
            response = await client.post(
                upload_url,
                headers=headers,
                content=file_content
            )

            if response.status_code not in [200, 201]:
                raise Exception(f"Upload failed with status {response.status_code}: {response.text}")

            logger.info(f"Large file upload successful: {file_path}")
            return response.json()

    def generate_signed_url(
        self,
        bucket: str,
        file_path: str,
        expires_in: int = 3600
    ) -> Optional[str]:
        if not self.is_available():
            return None

        try:
            result = self.supabase_client.storage.from_(bucket).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )

            if isinstance(result, dict) and 'signedURL' in result:
                return result['signedURL']

            logger.error(f"Unexpected signed URL response: {result}")
            return None

        except Exception as e:
            logger.error(f"Failed to generate signed URL for {file_path}: {e}")
            return None

    def delete_file(
        self,
        bucket: str,
        file_path: str
    ) -> bool:
        if not self.is_available():
            return False

        try:
            result = self.supabase_client.storage.from_(bucket).remove([file_path])
            logger.info(f"Deleted {file_path} from {bucket}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {file_path} from {bucket}: {e}")
            return False

    def get_public_url(
        self,
        bucket: str,
        file_path: str
    ) -> Optional[str]:
        if not self.is_available():
            return None

        try:
            return self.supabase_client.storage.from_(bucket).get_public_url(file_path)
        except Exception as e:
            logger.error(f"Failed to get public URL for {file_path}: {e}")
            return None

    async def download_file(
        self,
        bucket: str,
        file_path: str
    ) -> Optional[bytes]:
        """Download a file from Supabase storage"""
        if not self.is_available():
            logger.error("Supabase storage not available")
            return None

        try:
            # Download file content
            result = self.supabase_client.storage.from_(bucket).download(file_path)
            logger.info(f"Successfully downloaded {file_path} from {bucket}")
            return result
        except Exception as e:
            logger.error(f"Failed to download {file_path} from {bucket}: {e}")
            return None

storage_service = StorageService()