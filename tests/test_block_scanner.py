from dataclasses import dataclass

import pytest

from src.mev.block_scanner import BlockScanner


@dataclass
class FakeSwap:
    transaction_index: int
    log_index: int


class FakeEth:

    def __init__(self):

        self.block_number = 100

    def get_block(
        self,
        block_number,
        full_transactions=False,
    ):

        return {
            "number": block_number,
            "transactions": [
                "tx1",
                "tx2",
            ],
        }

    def get_transaction_receipt(
        self,
        tx_hash,
    ):

        return {
            "transactionHash": tx_hash,
        }


class FakeWeb3:

    def __init__(self):

        self.eth = FakeEth()


def test_latest_block():

    scanner = BlockScanner(
        FakeWeb3()
    )

    assert scanner.get_latest_block() == 100


def test_get_block():

    scanner = BlockScanner(
        FakeWeb3()
    )

    block = scanner.get_block(
        50
    )

    assert len(
        block["transactions"]
    ) == 2


def test_scan_block(monkeypatch):

    scanner = BlockScanner(
        FakeWeb3()
    )

    def fake_detector(receipt):

        if receipt["transactionHash"] == "tx1":

            return [
                FakeSwap(
                    transaction_index=1,
                    log_index=5,
                ),
                FakeSwap(
                    transaction_index=1,
                    log_index=2,
                ),
            ]

        return []

    monkeypatch.setattr(
        "src.mev.block_scanner.detect_swaps_from_receipt",
        fake_detector,
    )

    result = scanner.scan_block(
        50
    )

    assert result.block_number == 50
    assert result.transaction_count == 2
    assert result.swap_count == 2

    # Must be sorted by log index.
    assert (
        result.swaps[0].log_index
        == 2
    )

    assert (
        result.swaps[1].log_index
        == 5
    )


def test_scan_range(monkeypatch):

    scanner = BlockScanner(
        FakeWeb3()
    )

    monkeypatch.setattr(
        scanner,
        "scan_block",
        lambda block_number: type(
            "Result",
            (),
            {
                "block_number": block_number,
                "transaction_count": 2,
                "swap_count": 1,
                "swaps": [1],
            },
        )(),
    )

    results = scanner.scan_range(
        start_block=10,
        end_block=12,
    )

    assert len(results) == 3

    assert [
        result.block_number
        for result in results
    ] == [10, 11, 12]


def test_scan_range_invalid_start():

    scanner = BlockScanner(
        FakeWeb3()
    )

    with pytest.raises(
        ValueError
    ):

        scanner.scan_range(
            start_block=-1,
            end_block=10,
        )


def test_scan_range_invalid_order():

    scanner = BlockScanner(
        FakeWeb3()
    )

    with pytest.raises(
        ValueError
    ):

        scanner.scan_range(
            start_block=10,
            end_block=5,
        )


def test_scan_range_summary(monkeypatch):

    scanner = BlockScanner(
        FakeWeb3()
    )

    monkeypatch.setattr(
        scanner,
        "scan_range",
        lambda start_block, end_block: [
            type(
                "Result",
                (),
                {
                    "transaction_count": 10,
                    "swap_count": 2,
                },
            )(),
            type(
                "Result",
                (),
                {
                    "transaction_count": 20,
                    "swap_count": 3,
                },
            )(),
        ],
    )

    summary = scanner.scan_range_summary(
        start_block=100,
        end_block=101,
    )

    assert summary == {
        "start_block": 100,
        "end_block": 101,
        "blocks_scanned": 2,
        "transactions": 30,
        "swaps": 5,
    }