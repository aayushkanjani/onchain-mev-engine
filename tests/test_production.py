from __future__ import annotations

import asyncio

from src.production.market_state import MarketState
from src.production.metrics import Metrics
from src.production.opportunity_queue import (
    OpportunityQueue,
)


def test_market_state_persistence(tmp_path):

    database = tmp_path / "state.db"

    state = MarketState(
        database_path=database
    )

    state.save_block(
        block_number=100,
        transaction_count=50,
        swap_count=3,
        processed_at=123.0,
        latency_ms=12.5,
    )

    result = state.get_block(
        100
    )

    assert result is not None

    assert result["block_number"] == 100

    assert result["transaction_count"] == 50

    assert result["swap_count"] == 3

    assert result["latency_ms"] == 12.5

    assert (
        state.latest_processed_block()
        == 100
    )

    assert (
        state.count_blocks()
        == 1
    )


def test_market_state_multiple_blocks(tmp_path):

    database = tmp_path / "state.db"

    state = MarketState(
        database_path=database
    )

    for block_number in range(
        100,
        105,
    ):
        state.save_block(
            block_number=block_number,
            transaction_count=10,
            swap_count=1,
            processed_at=123.0,
            latency_ms=5.0,
        )

    assert (
        state.latest_processed_block()
        == 104
    )

    assert (
        state.count_blocks()
        == 5
    )


def test_metrics():

    metrics = Metrics()

    metrics.record_block(
        swap_count=2,
        latency_ms=10.0,
    )

    metrics.record_block(
        swap_count=3,
        latency_ms=20.0,
    )

    snapshot = metrics.snapshot()

    assert snapshot.blocks_processed == 2

    assert snapshot.swaps_detected == 5

    assert snapshot.failures == 0

    assert snapshot.total_latency_ms == 30.0

    assert snapshot.average_latency_ms == 15.0

    assert snapshot.last_latency_ms == 20.0


def test_metrics_failure():

    metrics = Metrics()

    metrics.record_failure()

    metrics.record_failure()

    snapshot = metrics.snapshot()

    assert snapshot.failures == 2


def test_opportunity_queue():

    async def run_test():

        queue = OpportunityQueue(
            max_size=10
        )

        await queue.put(
            "opportunity-1"
        )

        await queue.put(
            "opportunity-2"
        )

        assert queue.qsize() == 2

        first = await queue.get()

        assert first == "opportunity-1"

        queue.task_done()

        second = await queue.get()

        assert second == "opportunity-2"

        queue.task_done()

        assert queue.empty()

    asyncio.run(
        run_test()
    )


def test_opportunity_queue_join():

    async def run_test():

        queue = OpportunityQueue(
            max_size=10
        )

        await queue.put(
            "opportunity"
        )

        item = await queue.get()

        assert item == "opportunity"

        queue.task_done()

        await queue.join()

        assert queue.empty()

    asyncio.run(
        run_test()
    )


def test_block_stream_validation():

    from src.production.block_stream import BlockStream

    class FakeClient:
        def latest_block(self):
            return 100

    try:
        BlockStream(
            client=FakeClient(),
            poll_interval=0,
        )

        assert False

    except ValueError:
        assert True


def test_market_state_replaces_block(tmp_path):

    database = tmp_path / "state.db"

    state = MarketState(
        database_path=database
    )

    state.save_block(
        block_number=100,
        transaction_count=10,
        swap_count=1,
        processed_at=1.0,
        latency_ms=5.0,
    )

    state.save_block(
        block_number=100,
        transaction_count=20,
        swap_count=2,
        processed_at=2.0,
        latency_ms=7.0,
    )

    assert (
        state.count_blocks()
        == 1
    )

    result = state.get_block(
        100
    )

    assert result["transaction_count"] == 20

    assert result["swap_count"] == 2

    assert result["latency_ms"] == 7.0