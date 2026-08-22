from __future__ import annotations

import os

from web3 import Web3

from src.mev.block_scanner import BlockScanner


RPC_URL = os.getenv(
    "ETH_RPC_URL",
)


def create_web3() -> Web3:
    """
    Create an Ethereum RPC connection.
    """

    if not RPC_URL:
        raise RuntimeError(
            "ETH_RPC_URL environment variable is not set"
        )

    web3 = Web3(
        Web3.HTTPProvider(
            RPC_URL
        )
    )

    if not web3.is_connected():
        raise ConnectionError(
            "Could not connect to Ethereum RPC"
        )

    return web3


def print_block_result(result) -> None:

    print()
    print("=" * 70)
    print(
        f"BLOCK {result.block_number}"
    )
    print("=" * 70)

    print(
        f"Transactions: {result.transaction_count}"
    )

    print(
        f"Detected swaps: {result.swap_count}"
    )

    if not result.swaps:
        return

    print()
    print("-" * 70)

    for index, swap in enumerate(
        result.swaps,
        start=1,
    ):

        print(
            f"Swap #{index}"
        )

        print(
            f"  {swap}"
        )


def main():

    web3 = create_web3()

    scanner = BlockScanner(
        web3
    )

    latest_block = (
        scanner.get_latest_block()
    )

    print(
        "=" * 70
    )
    print(
        "MEV DETECTION — HISTORICAL BLOCK SCANNER"
    )
    print(
        "=" * 70
    )

    print(
        f"Latest block: {latest_block}"
    )

    # ------------------------------------------------------------
    # Configuration
    #
    # Change this to scan any historical block.
    # ------------------------------------------------------------

    block_number = latest_block - 1

    print(
        f"Scanning block: {block_number}"
    )

    result = scanner.scan_block(
        block_number
    )

    print_block_result(
        result
    )


if __name__ == "__main__":
    main()