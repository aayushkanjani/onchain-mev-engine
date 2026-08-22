from __future__ import annotations

from web3 import Web3

from src.blockchain.events import (
    V2_SWAP_TOPIC,
    V3_SWAP_TOPIC,
)
from src.blockchain.swap_detection import (
    PoolMetadata,
    SwapDetector,
)


TOKEN0 = Web3.to_checksum_address(
    "0x0000000000000000000000000000000000000001"
)

TOKEN1 = Web3.to_checksum_address(
    "0x0000000000000000000000000000000000000002"
)

POOL_V2 = Web3.to_checksum_address(
    "0x0000000000000000000000000000000000000010"
)

POOL_V3 = Web3.to_checksum_address(
    "0x0000000000000000000000000000000000000020"
)

SENDER = Web3.to_checksum_address(
    "0x0000000000000000000000000000000000000030"
)

RECIPIENT = Web3.to_checksum_address(
    "0x0000000000000000000000000000000000000040"
)


def topic_address(
    address: str,
) -> bytes:

    return bytes.fromhex(
        "00" * 12
        + address.removeprefix("0x")
    )


def word(
    value: int,
) -> bytes:

    return value.to_bytes(
        32,
        byteorder="big",
    )


def signed_word(
    value: int,
) -> bytes:

    return value.to_bytes(
        32,
        byteorder="big",
        signed=True,
    )


def make_v2_log():

    data = b"".join(
        [
            word(1_000),
            word(0),
            word(0),
            word(2_000),
        ]
    )

    return {
        "address": POOL_V2,
        "topics": [
            bytes.fromhex(
                V2_SWAP_TOPIC.removeprefix("0x")
            ),
            topic_address(SENDER),
            topic_address(RECIPIENT),
        ],
        "data": data,
        "blockNumber": 100,
        "transactionHash": bytes.fromhex(
            "11" * 32
        ),
        "logIndex": 5,
    }


def make_v3_log():

    data = b"".join(
        [
            signed_word(1_000),
            signed_word(-2_000),
            word(2**96),
            word(123_456),
            signed_word(100),
        ]
    )

    return {
        "address": POOL_V3,
        "topics": [
            bytes.fromhex(
                V3_SWAP_TOPIC.removeprefix("0x")
            ),
            topic_address(SENDER),
            topic_address(RECIPIENT),
        ],
        "data": data,
        "blockNumber": 101,
        "transactionHash": bytes.fromhex(
            "22" * 32
        ),
        "logIndex": 3,
    }


def create_detector():

    return SwapDetector(
        {
            "v2": PoolMetadata(
                address=POOL_V2,
                dex="Uniswap",
                version="V2",
                token0=TOKEN0,
                token1=TOKEN1,
            ),
            "v3": PoolMetadata(
                address=POOL_V3,
                dex="Uniswap",
                version="V3",
                token0=TOKEN0,
                token1=TOKEN1,
                fee=500,
                tick_spacing=10,
            ),
        }
    )


def test_classifies_v2_swap():

    detector = create_detector()

    log = make_v2_log()

    assert (
        detector.classify_log(log)
        == "V2"
    )


def test_classifies_v3_swap():

    detector = create_detector()

    log = make_v3_log()

    assert (
        detector.classify_log(log)
        == "V3"
    )


def test_detects_v2_swap():

    detector = create_detector()

    events = detector.detect_from_receipt(
        {
            "logs": [
                make_v2_log()
            ]
        }
    )

    assert len(events) == 1

    event = events[0]

    assert event.version == "V2"

    assert event.dex == "Uniswap"

    assert event.token_in == TOKEN0

    assert event.token_out == TOKEN1

    assert event.amount_in == 1_000

    assert event.amount_out == 2_000


def test_detects_v3_swap():

    detector = create_detector()

    events = detector.detect_from_receipt(
        {
            "logs": [
                make_v3_log()
            ]
        }
    )

    assert len(events) == 1

    event = events[0]

    assert event.version == "V3"

    assert event.dex == "Uniswap"

    assert event.token_in == TOKEN0

    assert event.token_out == TOKEN1

    assert event.amount_in == 1_000

    assert event.amount_out == 2_000

    assert event.sqrt_price_x96 == 2**96

    assert event.liquidity == 123_456

    assert event.tick == 100


def test_ignores_unknown_pool():

    detector = SwapDetector()

    log = make_v2_log()

    assert (
        detector.decode_log(log)
        is None
    )


def test_ignores_non_swap_event():

    detector = create_detector()

    log = make_v2_log()

    log["topics"] = [
        bytes.fromhex(
            "33" * 32
        )
    ]

    assert (
        detector.decode_log(log)
        is None
    )


def test_events_are_sorted_by_log_index():

    detector = create_detector()

    first = make_v2_log()
    second = make_v2_log()

    first["logIndex"] = 10
    second["logIndex"] = 2

    events = detector.detect_from_receipt(
        {
            "logs": [
                first,
                second,
            ]
        }
    )

    assert [
        event.log_index
        for event in events
    ] == [2, 10]