from __future__ import annotations

from dataclasses import dataclass

from src.mev_detection import create_detector


# ============================================================
# MODULE-LEVEL SWAP DETECTOR
# ============================================================

_detector = create_detector()


def detect_swaps_from_receipt(receipt):
    """
    Detect supported Uniswap swaps from a single transaction
    receipt.

    Kept at module level so tests can monkeypatch this function.
    """
    return _detector.detect_from_receipts([receipt])


# ============================================================
# RESULT
# ============================================================

@dataclass
class BlockScanResult:
    """
    Result of scanning a single Ethereum block.
    """

    block_number: int
    transaction_count: int
    swap_count: int
    swaps: list


# ============================================================
# BLOCK SCANNER
# ============================================================

class BlockScanner:
    """
    Scan Ethereum blocks and detect Uniswap swap events.

    Architecture:

        Ethereum RPC
             ↓
        BlockScanner
             ↓
        Transaction Receipts
             ↓
        detect_swaps_from_receipt()
             ↓
        Swap Events
    """

    def __init__(self, web3):
        """
        Initialize the block scanner.

        Parameters
        ----------
        web3:
            Web3-compatible Ethereum client.
        """
        self.web3 = web3

    # ========================================================
    # BLOCK
    # ========================================================

    def get_latest_block(self) -> int:
        """
        Return the latest Ethereum block number.
        """
        return self.web3.eth.block_number

    def get_block(self, block_number: int):
        """
        Retrieve a block with transaction hashes.
        """
        return self.web3.eth.get_block(
            block_number,
            full_transactions=False,
        )

    # ========================================================
    # RECEIPT
    # ========================================================

    def get_transaction_receipt(self, tx_hash):
        """
        Retrieve one transaction receipt.
        """
        return self.web3.eth.get_transaction_receipt(tx_hash)

    # ========================================================
    # SINGLE BLOCK
    # ========================================================

    def scan_block(self, block_number: int) -> BlockScanResult:
        """
        Scan one Ethereum block for Uniswap swap events.

        Steps:

            1. Fetch block
            2. Iterate transactions
            3. Fetch transaction receipts
            4. Detect swaps
            5. Sort swaps by blockchain execution order
            6. Return BlockScanResult
        """

        if block_number < 0:
            raise ValueError(
                "block_number must be non-negative"
            )

        # Fetch block
        block = self.get_block(block_number)

        transactions = block["transactions"]

        swaps = []

        # Process every transaction
        for tx_hash in transactions:
            receipt = self.get_transaction_receipt(tx_hash)

            detected = detect_swaps_from_receipt(receipt)

            if detected:
                swaps.extend(detected)

        # Preserve blockchain ordering.
        #
        # Events are ordered by:
        #   1. transaction index
        #   2. log index
        swaps.sort(
            key=lambda event: (
                getattr(event, "transaction_index", 0),
                getattr(event, "log_index", 0),
            )
        )

        return BlockScanResult(
            block_number=block_number,
            transaction_count=len(transactions),
            swap_count=len(swaps),
            swaps=swaps,
        )

    # ========================================================
    # BLOCK RANGE
    # ========================================================

    def scan_range(
        self,
        start_block: int,
        end_block: int,
    ) -> list[BlockScanResult]:
        """
        Scan an inclusive range of Ethereum blocks.

        Example:

            scan_range(20_000_000, 20_000_010)
        """

        if start_block < 0:
            raise ValueError(
                "start_block must be non-negative"
            )

        if end_block < start_block:
            raise ValueError(
                "end_block must be >= start_block"
            )

        results = []

        for block_number in range(
            start_block,
            end_block + 1,
        ):
            results.append(
                self.scan_block(block_number)
            )

        return results

    # ========================================================
    # RANGE SUMMARY
    # ========================================================

    def scan_range_summary(
        self,
        start_block: int,
        end_block: int,
    ) -> dict[str, int]:
        """
        Scan a block range and return aggregate statistics.
        """

        results = self.scan_range(
            start_block=start_block,
            end_block=end_block,
        )

        transaction_count = sum(
            result.transaction_count
            for result in results
        )

        swap_count = sum(
            result.swap_count
            for result in results
        )

        return {
            "start_block": start_block,
            "end_block": end_block,
            "blocks_scanned": len(results),
            "transactions": transaction_count,
            "swaps": swap_count,
        }