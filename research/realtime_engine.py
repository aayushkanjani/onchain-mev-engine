from __future__ import annotations

import os
import time

from src.blockchain.client import EthereumClient
from src.mev.block_stream import BlockStream
from src.mev_detection import create_detector


def main() -> None:
    print("=" * 70)
    print("ON-CHAIN MEV ENGINE — REAL-TIME BLOCK STREAM")
    print("=" * 70)

    client = EthereumClient()

    detector = create_detector()

    start_block_env = os.getenv(
        "MEV_START_BLOCK"
    )

    max_blocks_env = os.getenv(
        "MEV_MAX_BLOCKS",
        "1",
    )

    confirmations_env = os.getenv(
        "MEV_CONFIRMATIONS",
        "0",
    )

    poll_interval_env = os.getenv(
        "MEV_POLL_INTERVAL",
        "1.0",
    )

    start_block = (
        int(start_block_env)
        if start_block_env
        else client.latest_block()
    )

    max_blocks = int(
        max_blocks_env
    )

    confirmations = int(
        confirmations_env
    )

    poll_interval = float(
        poll_interval_env
    )

    stream = BlockStream(
        client=client,
        detector=detector,
        start_block=start_block,
        poll_interval=poll_interval,
        confirmations=confirmations,
    )

    print()
    print(
        f"Starting block: {start_block}"
    )

    print(
        f"Maximum blocks: {max_blocks}"
    )

    print(
        f"Confirmations:  {confirmations}"
    )

    print(
        f"Poll interval:  {poll_interval}s"
    )

    print()
    print(
        "Using direct Ethereum log ingestion."
    )

    print(
        "No transaction-receipt scan is performed."
    )

    print()
    print("-" * 70)

    total_blocks = 0
    total_swaps = 0

    started = time.perf_counter()

    for result in stream.stream(
        max_blocks=max_blocks
    ):
        total_blocks += 1
        total_swaps += result.swap_count

        print()
        print(
            f"Block: {result.block_number}"
        )

        print(
            f"Swaps: {result.swap_count}"
        )

        for event in result.swaps:

            print(
                f"  TX:       {event.tx_hash}"
            )

            print(
                f"  DEX:      {event.dex} "
                f"{event.version}"
            )

            print(
                f"  Pool:     {event.pool_address}"
            )

            print(
                f"  Token in: {event.token_in}"
            )

            print(
                f"  Token out:{event.token_out}"
            )

            print(
                f"  Amount in:{event.amount_in}"
            )

            print(
                f"  Amount out:{event.amount_out}"
            )

            if event.version == "V3":

                print(
                    f"  Tick:     {event.tick}"
                )

                print(
                    f"  Liquidity:{event.liquidity}"
                )

            print(
                f"  Log:      {event.log_index}"
            )

    elapsed = (
        time.perf_counter()
        - started
    )

    print()
    print("-" * 70)
    print("STREAM METRICS")
    print("-" * 70)

    print(
        f"Blocks processed: {total_blocks}"
    )

    print(
        f"Swaps detected:   {total_swaps}"
    )

    print(
        f"Elapsed time:     {elapsed:.2f} s"
    )

    if total_blocks > 0:

        print(
            f"Avg/block:        "
            f"{elapsed / total_blocks:.2f} s"
        )

    print()
    print(
        "Real-time block stream test complete."
    )


if __name__ == "__main__":
    main()