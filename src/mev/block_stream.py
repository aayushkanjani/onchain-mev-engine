from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterator

from src.blockchain.client import EthereumClient
from src.blockchain.swap_detection import SwapDetector


# ============================================================
# STREAMED BLOCK
# ============================================================

@dataclass(frozen=True)
class StreamedBlock:
    """
    Normalized result produced by the real-time block stream.
    """

    block_number: int
    swap_count: int
    swaps: list


# ============================================================
# BLOCK STREAM
# ============================================================

class BlockStream:
    """
    Continuously observe Ethereum blocks and ingest relevant
    swap logs.

    Milestone 9 architecture:

        Ethereum RPC
             ↓
        latest block
             ↓
        BlockStream
             ↓
        eth_getLogs
             ↓
        SwapDetector
             ↓
        StreamedBlock
    """

    def __init__(
        self,
        client: EthereumClient,
        detector: SwapDetector,
        start_block: int | None = None,
        poll_interval: float = 1.0,
        confirmations: int = 0,
    ):
        if poll_interval <= 0:
            raise ValueError(
                "poll_interval must be > 0"
            )

        if confirmations < 0:
            raise ValueError(
                "confirmations must be >= 0"
            )

        if start_block is not None and start_block < 0:
            raise ValueError(
                "start_block must be non-negative"
            )

        self.client = client
        self.detector = detector

        self.poll_interval = poll_interval
        self.confirmations = confirmations

        self.next_block = start_block

        self.blocks_processed = 0
        self.swaps_detected = 0
        self.last_block: int | None = None

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def validate_block_range(
        start_block: int,
        end_block: int,
    ) -> None:
        """
        Validate an inclusive block range.
        """

        if start_block < 0:
            raise ValueError(
                "start_block must be non-negative"
            )

        if end_block < start_block:
            raise ValueError(
                "end_block must be >= start_block"
            )

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def initialize(
        self,
    ) -> int:
        """
        Initialize the stream cursor.

        If start_block was not provided, begin at the current
        latest block.
        """

        if self.next_block is None:
            self.next_block = (
                self.client.latest_block()
            )

        return self.next_block

    # ========================================================
    # LOG INGESTION
    # ========================================================

    def scan_block(
        self,
        block_number: int,
    ) -> StreamedBlock:
        """
        Scan one block using direct log retrieval.

        This avoids fetching every transaction receipt.
        """

        if block_number < 0:
            raise ValueError(
                "block_number must be non-negative"
            )

        logs = self.client.get_logs_for_pools(
            from_block=block_number,
            to_block=block_number,
            pool_addresses=(
                self.detector.pool_addresses()
            ),
            topics=(
                self.detector.supported_swap_topics()
            ),
        )

        swaps = self.detector.detect_from_logs(
            logs
        )

        result = StreamedBlock(
            block_number=block_number,
            swap_count=len(swaps),
            swaps=swaps,
        )

        self.blocks_processed += 1
        self.swaps_detected += len(swaps)
        self.last_block = block_number

        return result

    # ========================================================
    # CATCH UP
    # ========================================================

    def catch_up(
        self,
    ) -> list[StreamedBlock]:
        """
        Process all blocks currently available up to the
        confirmation boundary.

        Example:

            next_block = 100
            latest = 105
            confirmations = 2

        Process:

            100
            101
            102
            103

        and leave 104/105 unprocessed until they are sufficiently
        confirmed.
        """

        self.initialize()

        latest = self.client.latest_block()

        safe_latest = (
            latest
            - self.confirmations
        )

        if safe_latest < self.next_block:
            return []

        results: list[StreamedBlock] = []

        while self.next_block <= safe_latest:

            result = self.scan_block(
                self.next_block
            )

            results.append(
                result
            )

            self.next_block += 1

        return results

    # ========================================================
    # SINGLE POLL
    # ========================================================

    def poll_once(
        self,
    ) -> list[StreamedBlock]:
        """
        Process all currently available blocks once.
        """

        return self.catch_up()

    # ========================================================
    # CONTINUOUS STREAM
    # ========================================================

    def stream(
        self,
        max_blocks: int | None = None,
    ) -> Iterator[StreamedBlock]:
        """
        Continuously process new Ethereum blocks.

        max_blocks is useful for tests and milestone demos.

        If max_blocks is None, the stream continues forever.
        """

        processed = 0

        self.initialize()

        while True:

            results = self.catch_up()

            for result in results:

                yield result

                processed += 1

                if (
                    max_blocks is not None
                    and processed >= max_blocks
                ):
                    return

            if (
                max_blocks is not None
                and processed >= max_blocks
            ):
                return

            time.sleep(
                self.poll_interval
            )

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
        next_block: int | None = None,
    ) -> None:
        """
        Reset the stream cursor and counters.
        """

        self.next_block = next_block

        self.blocks_processed = 0
        self.swaps_detected = 0
        self.last_block = None