from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class MetricsSnapshot:
    """
    Snapshot of production-engine metrics.
    """

    blocks_processed: int
    swaps_detected: int
    failures: int
    total_latency_ms: float
    average_latency_ms: float
    last_latency_ms: float
    started_at: float


@dataclass
class Metrics:
    """
    Lightweight in-process monitoring.

    Tracks:

        blocks processed
        swaps detected
        failures
        processing latency
    """

    blocks_processed: int = 0
    swaps_detected: int = 0
    failures: int = 0

    total_latency_ms: float = 0.0
    last_latency_ms: float = 0.0

    started_at: float = field(
        default_factory=time.perf_counter
    )

    def record_block(
        self,
        swap_count: int,
        latency_ms: float,
    ) -> None:
        """
        Record one successfully processed block.
        """

        self.blocks_processed += 1

        self.swaps_detected += swap_count

        self.total_latency_ms += latency_ms

        self.last_latency_ms = latency_ms

    def record_failure(self) -> None:
        """
        Record one processing failure.
        """

        self.failures += 1

    @property
    def average_latency_ms(self) -> float:
        """
        Return average block-processing latency.
        """

        if self.blocks_processed == 0:
            return 0.0

        return (
            self.total_latency_ms
            / self.blocks_processed
        )

    def snapshot(self) -> MetricsSnapshot:
        """
        Return a stable metrics snapshot.
        """

        return MetricsSnapshot(
            blocks_processed=self.blocks_processed,
            swaps_detected=self.swaps_detected,
            failures=self.failures,
            total_latency_ms=self.total_latency_ms,
            average_latency_ms=self.average_latency_ms,
            last_latency_ms=self.last_latency_ms,
            started_at=self.started_at,
        )