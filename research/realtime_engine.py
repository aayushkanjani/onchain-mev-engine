from __future__ import annotations

import os
import time

from src.blockchain.client import EthereumClient
from src.mev.block_stream import BlockStream
from src.mev.opportunity import (
    MarketObservation,
    OpportunityDetector,
)
from src.mev_detection import create_detector


def main() -> None:

    print("=" * 70)
    print("ON-CHAIN MEV ENGINE — REAL-TIME MEV PIPELINE")
    print("=" * 70)

    client = EthereumClient()

    detector = create_detector()

    opportunity_detector = OpportunityDetector(
        min_spread_percent=float(
            os.getenv(
                "MEV_MIN_SPREAD_PERCENT",
                "0.10",
            )
        )
    )

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
        f"Starting block:  {start_block}"
    )

    print(
        f"Maximum blocks:  {max_blocks}"
    )

    print(
        f"Confirmations:   {confirmations}"
    )

    print(
        f"Poll interval:   {poll_interval}s"
    )

    print(
        f"Min spread:      "
        f"{opportunity_detector.min_spread_percent}%"
    )

    print()

    print(
        "Pipeline:"
    )

    print(
        "Ethereum logs"
    )

    print(
        "      ↓"
    )

    print(
        "Swap detection"
    )

    print(
        "      ↓"
    )

    print(
        "Market observations"
    )

    print(
        "      ↓"
    )

    print(
        "MEV opportunity detection"
    )

    print()

    total_blocks = 0
    total_swaps = 0
    total_opportunities = 0

    started = time.perf_counter()

    for result in stream.stream(
        max_blocks=max_blocks
    ):

        total_blocks += 1

        total_swaps += (
            result.swap_count
        )

        print()
        print("-" * 70)

        print(
            f"Block: {result.block_number}"
        )

        print(
            f"Swaps detected: "
            f"{result.swap_count}"
        )

        observations: list[
            MarketObservation
        ] = []

        # ----------------------------------------------------
        # Convert detected swaps into observations.
        #
        # For this milestone, only swaps with a usable
        # positive amount ratio are considered.
        # ----------------------------------------------------

        for event in result.swaps:

            if (
                event.amount_in is None
                or event.amount_out is None
            ):
                continue

            if event.amount_in <= 0:
                continue

            if event.amount_out <= 0:
                continue

            pool = detector.get_pool(
                event.pool_address
            )

            if pool is None:
                continue

            price = (
                float(event.amount_out)
                / float(event.amount_in)
            )

            try:

                observation = (
                    opportunity_detector
                    .observation_from_price(
                        pool=pool,
                        price_token1_per_token0=price,
                        block_number=(
                            getattr(
                                event,
                                "block_number",
                                result.block_number,
                            )
                        ),
                        transaction_index=(
                            getattr(
                                event,
                                "transaction_index",
                                None,
                            )
                        ),
                        log_index=(
                            getattr(
                                event,
                                "log_index",
                                None,
                            )
                        ),
                    )
                )

            except ValueError:

                continue

            observations.append(
                observation
            )

        opportunities = (
            opportunity_detector.detect(
                observations
            )
        )

        total_opportunities += len(
            opportunities
        )

        print(
            f"Market observations: "
            f"{len(observations)}"
        )

        print(
            f"MEV opportunities:   "
            f"{len(opportunities)}"
        )

        for opportunity in opportunities:

            print()
            print(
                "MEV OPPORTUNITY"
            )

            print(
                f"  Buy:       "
                f"{opportunity.buy_pool}"
            )

            print(
                f"  Sell:      "
                f"{opportunity.sell_pool}"
            )

            print(
                f"  Buy price: "
                f"{opportunity.buy_price:.12f}"
            )

            print(
                f"  Sell price:"
                f" {opportunity.sell_price:.12f}"
            )

            print(
                f"  Spread:    "
                f"{opportunity.gross_spread_percent:.4f}%"
            )

    elapsed = (
        time.perf_counter()
        - started
    )

    print()
    print("=" * 70)
    print("REAL-TIME ENGINE METRICS")
    print("=" * 70)

    print(
        f"Blocks processed:     "
        f"{total_blocks}"
    )

    print(
        f"Swaps detected:       "
        f"{total_swaps}"
    )

    print(
        f"Opportunities found:  "
        f"{total_opportunities}"
    )

    print(
        f"Elapsed time:         "
        f"{elapsed:.2f} s"
    )

    if total_blocks > 0:

        print(
            f"Average block time:   "
            f"{elapsed / total_blocks:.2f} s"
        )

    print()
    print(
        "Real-time MEV pipeline complete."
    )


if __name__ == "__main__":
    main()