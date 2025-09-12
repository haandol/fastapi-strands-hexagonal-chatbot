from typing import Dict, Optional, override, List

import ulid
import boto3
from strands.types.session import SessionMessage
from strands.session.s3_session_manager import S3SessionManager

from ports.adapters.secondary import SessionAdapter
from utils.logger import logger


class StrandsS3SessionAdapter(SessionAdapter):
    def __init__(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        aws_profile_name: Optional[str] = None,
    ):
        self.bucket = bucket
        self.prefix = prefix or ""
        self.boto_session = boto3.Session(
            profile_name=aws_profile_name,
        )
        self.s3_client = self.boto_session.client("s3")

        self._sessions: Dict[str, S3SessionManager] = {}

    @property
    def sessions(self) -> Dict[str, S3SessionManager]:
        return self._sessions

    @override
    async def create_session(self, user_id: str) -> str:
        session_id = ulid.ulid()
        # Include user_id in the S3 prefix path, ensure no double slashes
        user_prefix = f"{self.prefix.rstrip('/')}/user_{user_id}/"
        self.sessions[session_id] = S3SessionManager(
            session_id=session_id,
            bucket=self.bucket,
            prefix=user_prefix,
            boto_session=self.boto_session,
        )
        logger.info("s3 session created", session_id=session_id, user_id=user_id)
        return session_id

    @override
    async def get_user_session_ids(self, user_id: str) -> List[str]:
        try:
            # List all objects under the user-specific prefix to find sessions
            user_prefix = f"{self.prefix.rstrip('/')}/user_{user_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=user_prefix,
            )

            # Extract session_id from key like: sessions/user_{user_id}/session_{session_id}/
            session_ids = set()
            for obj in response.get("Contents", []):
                key = obj["Key"]
                parts = key.split("/")
                for part in parts:
                    if part.startswith("session_"):
                        session_id = part.split("_", 1)[1]
                        session_ids.add(session_id)
                        break

            return list(session_ids)
        except Exception:
            logger.error(
                "error listing user sessions",
                user_id=user_id,
                exc_info=True,
                stack_info=True,
            )
            return []

    @override
    async def get_session(self, user_id: str, session_id: str) -> S3SessionManager:
        if session_id not in self.sessions:
            logger.info("s3 session not found, restore old session", session_id=session_id)
            try:
                user_prefix = f"{self.prefix.rstrip('/')}/user_{user_id}/"
                self.sessions[session_id] = S3SessionManager(
                    boto_session=self.boto_session,
                    session_id=session_id,
                    bucket=self.bucket,
                    prefix=user_prefix,
                )
            except Exception:
                logger.error(
                    "error restoring old session",
                    session_id=session_id,
                    exc_info=True,
                    stack_info=True,
                )
                raise

        return self.sessions[session_id]

    @override
    async def list_messages(self, user_id: str, session_id: str) -> List[SessionMessage]:
        session_manager = await self.get_session(user_id, session_id)
        try:
            return session_manager.list_messages(
                session_id=session_id,
                agent_id="default",
            )
        except Exception:
            logger.error(
                "error listing messages",
                session_id=session_id,
                exc_info=True,
                stack_info=True,
            )
            return []

    @override
    async def delete_session(self, user_id: str, session_id: str) -> None:
        if session_id not in self.sessions:
            logger.warn("s3 session not found", session_id=session_id)
            return

        del self.sessions[session_id]
        logger.info("s3 session deleted", session_id=session_id)

    @override
    async def cleanup(self) -> None:
        logger.info("🧹 cleaning up s3 session adapter")

        self.sessions.clear()

        logger.info("🧹 s3 session adapter cleaned up")
