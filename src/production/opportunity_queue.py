from __future__ import annotations

import asyncio
from typing import Any


class OpportunityQueue:
    """
    Asynchronous queue for MEV opportunities.

    The queue decouples detection from downstream processing.

    Architecture:

        detector
            ↓
        OpportunityQueue
            ↓
        consumer
    """

    def __init__(
        self,
        max_size: int = 10_000,
    ):
        if max_size <= 0:
            raise ValueError(
                "max_size must be positive"
            )

        self._queue: asyncio.Queue[Any] = (
            asyncio.Queue(
                maxsize=max_size
            )
        )

    async def put(
        self,
        opportunity: Any,
    ) -> None:
        """
        Add an opportunity to the queue.
        """

        await self._queue.put(
            opportunity
        )

    async def get(self) -> Any:
        """
        Retrieve the next opportunity.
        """

        return await self._queue.get()

    def task_done(self) -> None:
        """
        Mark the current queue item as processed.
        """

        self._queue.task_done()

    async def join(self) -> None:
        """
        Wait until all queued opportunities are processed.
        """

        await self._queue.join()

    def qsize(self) -> int:
        """
        Return the current queue size.
        """

        return self._queue.qsize()

    def empty(self) -> bool:
        """
        Return True if the queue is empty.
        """

        return self._queue.empty()

    def full(self) -> bool:
        """
        Return True if the queue is full.
        """

        return self._queue.full()