"""
notification.py

Sends notifications to members about loans, fines, and reservations.
Demonstrates: async function definitions, enums, type hints,
default argument values.
"""

from __future__ import annotations

import asyncio
from enum import Enum
from typing import List, Optional

from logger import get_logger

logger = get_logger()


class NotificationChannel(Enum):
    """Enumerates the supported notification delivery channels."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationService:
    """Handles composing and 'sending' notifications to members."""

    def __init__(self) -> None:
        self.sent_log: List[str] = []

    def build_message(
        self,
        member_name: str,
        subject: str,
        body: Optional[str] = None,
    ) -> str:
        """Compose a notification message, using a default body if none given."""
        if body is None:
            body = "Please check your library account for details."
        return f"Dear {member_name},\n{subject}\n{body}"

    async def send_async(
        self,
        member_name: str,
        subject: str,
        channel: NotificationChannel = NotificationChannel.EMAIL,
    ) -> bool:
        """
        Asynchronously send a notification to a member.

        Demonstrates: AsyncFunctionDef AST node, await expressions.
        """
        message = self.build_message(member_name, subject)
        await asyncio.sleep(0)  # simulate non-blocking I/O
        self.sent_log.append(message)
        logger.info(
            "Sent %s notification to %s: %s", channel.value, member_name, subject
        )
        return True

    async def notify_overdue(self, member_name: str, days_overdue: int) -> bool:
        """Send an overdue notice, escalating the channel if very late."""
        channel = (
            NotificationChannel.SMS if days_overdue > 7 else NotificationChannel.EMAIL
        )
        subject = f"Your loan is {days_overdue} day(s) overdue"
        return await self.send_async(member_name, subject, channel)

    async def notify_many(self, recipients: List[str], subject: str) -> int:
        """
        Send the same notification to multiple recipients concurrently.

        Demonstrates: asyncio.gather, list comprehension, for loop.
        """
        tasks = [self.send_async(name, subject) for name in recipients]
        results = await asyncio.gather(*tasks)
        return sum(1 for result in results if result)
