from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from src.mev.block_scanner import BlockScanner

from .block_stream import BlockStream
from .market_state import MarketState
from .metrics import Metrics
from .opportunity_queue import OpportunityQueue


@dataclass
class ProcessedBlock:
    """
    Result of processing one block.
    """

    block_number: int
    transaction_count: int
    swap_count: int
    latency_ms: float


class ProductionEngine:
    """
    Production-oriented MEV processing engine.

    Responsibilities:

        block streaming
        asynchronous block processing
        persistent state
        opportunity queue
        metrics
        failure handling
    """

    def __init__(
        self,
        web3,
        client,
        database_path: str = "data/market_state.db",
        poll_interval: float = 1.0,
        queue_size: int = 10_000,
        max_retries: int = 3,
        retry_delay: float = 0.5,
    ):
        if max_retries < 0:
            raise ValueError(
                "max_retries must be non-negative"
            )

        if retry_delay <= 0:
            raise ValueError(
                "retry_delay must be positive"
            )

        self.web3 = web3
        self.client = client

        self.scanner = BlockScanner(
            web3
        )

        self.stream = BlockStream(
            client=client,
            poll_interval=poll_interval,
        )

        self.state = MarketState(
            database_path=database_path
        )

        self.opportunity_queue = OpportunityQueue(
            max_size=queue_size
        )

        self.metrics = Metrics()

        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self._running = False

    async def process_block(
        self,
        block_number: int,
    ) -> ProcessedBlock:
        """
        Process a single Ethereum block asynchronously.

        The existing synchronous BlockScanner is executed in a
        worker thread so the event loop remains responsive.
        """

        started = time.perf_counter()

        result = await asyncio.to_thread(
            self.scanner.scan_block,
            block_number,
        )

        latency_ms = (
            time.perf_counter()
            - started
        ) * 1000.0

        processed = ProcessedBlock(
            block_number=result.block_number,
            transaction_count=result.transaction_count,
            swap_count=result.swap_count,
            latency_ms=latency_ms,
        )

        # Persist block state.
        await asyncio.to_thread(
            self.state.save_block,
            result.block_number,
            result.transaction_count,
            result.swap_count,
            time.time(),
            latency_ms,
        )

        # Push detected swaps into the opportunity queue.
        for swap in result.swaps:
            await self.opportunity_queue.put(
                swap
            )

        self.metrics.record_block(
            swap_count=result.swap_count,
            latency_ms=latency_ms,
        )

        return processed

    async def process_block_with_retry(
        self,
        block_number: int,
    ) -> ProcessedBlock | None:
        """
        Process a block with bounded retries.

        Returns None if all retries fail.
        """

        attempts = 0

        while True:
            try:
                return await self.process_block(
                    block_number
                )

            except Exception:
                self.metrics.record_failure()

                if attempts >= self.max_retries:
                    return None

                attempts += 1

                await asyncio.sleep(
                    self.retry_delay
                )

    async def run(
        self,
        start_block: int | None = None,
        max_blocks: int | None = None,
    ) -> None:
        """
        Start the continuous production engine.

        Parameters
        ----------
        start_block:
            Optional starting block.

        max_blocks:
            Optional limit used mainly for testing/research.

            None means run continuously.
        """

        if max_blocks is not None:
            if max_blocks <= 0:
                raise ValueError(
                    "max_blocks must be positive"
                )

        self._running = True

        processed_blocks = 0

        async for block_number in self.stream.stream(
            start_block=start_block
        ):
            if not self._running:
                break

            await self.process_block_with_retry(
                block_number
            )

            processed_blocks += 1

            if (
                max_blocks is not None
                and processed_blocks >= max_blocks
            ):
                break

    def stop(self) -> None:
        """
        Stop the streaming loop after the current
        iteration finishes.
        """

        self._running = False

    async def consume_opportunities(
        self,
        max_items: int | None = None,
    ) -> list:
        """
        Consume queued opportunities.

        This method is intentionally simple for Milestone 8.

        Later milestones can replace this with:

            opportunity ranking
            profitability simulation
            execution simulation
        """

        opportunities = []

        while (
            max_items is None
            or len(opportunities) < max_items
        ):
            if self.opportunity_queue.empty():
                break

            opportunity = await self.opportunity_queue.get()

            opportunities.append(
                opportunity
            )

            self.opportunity_queue.task_done()

        return opportunities