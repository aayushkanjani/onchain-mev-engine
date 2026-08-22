from __future__ import annotations

import os

from web3 import Web3

from src.mev.block_scanner import BlockScanner


RPC_URL = os.getenv(
    "ETH_RPC_URL",
)


def main():

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

    scanner = BlockScanner(
        web3
    )

    latest = scanner.get_latest_block()

    # Scan the most recent 10 blocks.
    start_block = latest - 9
    end_block = latest

    print(
        "=" * 70
    )
    print(
        "MEV DETECTION — BLOCK RANGE"
    )
    print(
        "=" * 70
    )

    print(
        f"Range: {start_block} → {end_block}"
    )

    results = scanner.scan_range(
        start_block=start_block,
        end_block=end_block,
    )

    print()

    total_transactions = 0
    total_swaps = 0

    for result in results:

        total_transactions += (
            result.transaction_count
        )

        total_swaps += (
            result.swap_count
        )

        print(
            f"Block {result.block_number:<12} "
            f"txs={result.transaction_count:<4} "
            f"swaps={result.swap_count}"
        )

    print()
    print("-" * 70)

    print(
        f"Blocks scanned: {len(results)}"
    )

    print(
        f"Transactions:   {total_transactions}"
    )

    print(
        f"Swaps detected:  {total_swaps}"
    )


if __name__ == "__main__":
    main()