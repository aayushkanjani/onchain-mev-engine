from dataclasses import dataclass

import pytest

from src.mev.block_stream import (
    BlockStream,
    StreamedBlock,
)


@dataclass
class FakeSwap:
    block_number: int
    transaction_index: int
    log_index: int


class FakeDetector:
    def __init__(self):
        self.logs_seen = []

    def pool_addresses(self):
        return [
            "pool1",
            "pool2",
        ]

    def supported_swap_topics(self):
        return [
            "topic_v2",
            "topic_v3",
        ]

    def detect_from_logs(self, logs):
        self.logs_seen.extend(logs)

        swaps = []

        for log in logs:
            swaps.append(
                FakeSwap(
                    block_number=log["blockNumber"],
                    transaction_index=log[
                        "transactionIndex"
                    ],
                    log_index=log["logIndex"],
                )
            )

        return sorted(
            swaps,
            key=lambda event: (
                event.block_number,
                event.transaction_index,
                event.log_index,
            ),
        )


class FakeClient:
    def __init__(self):
        self.current_block = 100

        self.requests = []

    def latest_block(self):
        return self.current_block

    def get_logs_for_pools(
        self,
        from_block,
        to_block,
        pool_addresses,
        topics,
    ):
        self.requests.append(
            {
                "from_block": from_block,
                "to_block": to_block,
                "pool_addresses": pool_addresses,
                "topics": topics,
            }
        )

        if from_block == 100:
            return [
                {
                    "blockNumber": 100,
                    "transactionIndex": 2,
                    "logIndex": 5,
                },
                {
                    "blockNumber": 100,
                    "transactionIndex": 1,
                    "logIndex": 3,
                },
            ]

        return []


def test_validate_block_range():
    BlockStream.validate_block_range(
        10,
        20,
    )


def test_validate_block_range_invalid_start():

    with pytest.raises(ValueError):

        BlockStream.validate_block_range(
            -1,
            10,
        )


def test_validate_block_range_invalid_order():

    with pytest.raises(ValueError):

        BlockStream.validate_block_range(
            20,
            10,
        )


def test_invalid_poll_interval():

    with pytest.raises(ValueError):

        BlockStream(
            client=FakeClient(),
            detector=FakeDetector(),
            poll_interval=0,
        )


def test_invalid_confirmations():

    with pytest.raises(ValueError):

        BlockStream(
            client=FakeClient(),
            detector=FakeDetector(),
            confirmations=-1,
        )


def test_initialize_uses_latest_block():

    stream = BlockStream(
        client=FakeClient(),
        detector=FakeDetector(),
    )

    assert stream.initialize() == 100
    assert stream.next_block == 100


def test_scan_block_uses_log_ingestion():

    client = FakeClient()
    detector = FakeDetector()

    stream = BlockStream(
        client=client,
        detector=detector,
        start_block=100,
    )

    result = stream.scan_block(
        100
    )

    assert isinstance(
        result,
        StreamedBlock,
    )

    assert result.block_number == 100

    assert result.swap_count == 2

    assert [
        swap.log_index
        for swap in result.swaps
    ] == [3, 5]

    assert len(
        client.requests
    ) == 1

    request = client.requests[0]

    assert request[
        "from_block"
    ] == 100

    assert request[
        "to_block"
    ] == 100

    assert request[
        "pool_addresses"
    ] == [
        "pool1",
        "pool2",
    ]

    assert request[
        "topics"
    ] == [
        "topic_v2",
        "topic_v3",
    ]


def test_scan_block_updates_metrics():

    stream = BlockStream(
        client=FakeClient(),
        detector=FakeDetector(),
        start_block=100,
    )

    result = stream.scan_block(
        100
    )

    assert stream.blocks_processed == 1

    assert stream.swaps_detected == (
        result.swap_count
    )

    assert stream.last_block == 100


def test_catch_up_processes_confirmed_blocks():

    client = FakeClient()
    detector = FakeDetector()

    client.current_block = 103

    stream = BlockStream(
        client=client,
        detector=detector,
        start_block=100,
        confirmations=1,
    )

    results = stream.catch_up()

    assert [
        result.block_number
        for result in results
    ] == [
        100,
        101,
        102,
    ]

    assert stream.next_block == 103


def test_catch_up_waits_for_confirmation():

    client = FakeClient()
    detector = FakeDetector()

    client.current_block = 100

    stream = BlockStream(
        client=client,
        detector=detector,
        start_block=100,
        confirmations=2,
    )

    results = stream.catch_up()

    assert results == []

    assert stream.next_block == 100


def test_poll_once():

    client = FakeClient()
    detector = FakeDetector()

    stream = BlockStream(
        client=client,
        detector=detector,
        start_block=100,
    )

    results = stream.poll_once()

    assert len(results) == 1

    assert results[0].block_number == 100


def test_stream_limited():

    client = FakeClient()
    detector = FakeDetector()

    stream = BlockStream(
        client=client,
        detector=detector,
        start_block=100,
        poll_interval=0.001,
    )

    results = list(
        stream.stream(
            max_blocks=1
        )
    )

    assert len(results) == 1

    assert results[0].block_number == 100


def test_reset():

    stream = BlockStream(
        client=FakeClient(),
        detector=FakeDetector(),
        start_block=100,
    )

    stream.blocks_processed = 5
    stream.swaps_detected = 10
    stream.last_block = 104

    stream.reset(
        next_block=200
    )

    assert stream.next_block == 200
    assert stream.blocks_processed == 0
    assert stream.swaps_detected == 0
    assert stream.last_block is None