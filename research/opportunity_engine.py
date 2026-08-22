from __future__ import annotations

import os

from src.blockchain.client import EthereumClient
from src.mev.opportunity import (
    MarketObservation,
    OpportunityDetector,
)
from src.mev_detection import create_detector


def main() -> None:

    print("=" * 70)
    print("ON-CHAIN MEV ENGINE — OPPORTUNITY DETECTION")
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

    latest_block = client.latest_block()

    print()
    print(
        f"Latest block: {latest_block}"
    )

    print()
    print(
        "Registered pools:"
    )

    for address in detector.pool_addresses():

        pool = detector.get_pool(
            address
        )

        if pool is None:
            continue

        print(
            f"  {pool.dex} "
            f"{pool.version} "
            f"{pool.address}"
        )

    print()
    print(
        "This milestone demonstrates "
        "the opportunity detection layer."
    )

    print()
    print(
        "Market observations must be supplied "
        "from normalized pool state."
    )

    print()
    print("-" * 70)
    print("DEMO")
    print("-" * 70)

    pools = [
        detector.get_pool(
            address
        )
        for address in detector.pool_addresses()
    ]

    pools = [
        pool
        for pool in pools
        if pool is not None
    ]

    observations: list[
        MarketObservation
    ] = []

    # --------------------------------------------------------
    # Demonstration observations.
    #
    # These are intentionally synthetic.
    # The blockchain ingestion layer remains real.
    # --------------------------------------------------------

    if len(pools) >= 2:

        first = opportunity_detector.observation_from_price(
            pool=pools[0],
            price_token1_per_token0=0.000520,
            block_number=latest_block,
        )

        second = opportunity_detector.observation_from_price(
            pool=pools[1],
            price_token1_per_token0=0.000525,
            block_number=latest_block,
        )

        observations.extend(
            [
                first,
                second,
            ]
        )

    opportunities = opportunity_detector.detect(
        observations
    )

    print()

    print(
        f"Observations:  {len(observations)}"
    )

    print(
        f"Opportunities: {len(opportunities)}"
    )

    print()

    if not opportunities:

        print(
            "No arbitrage opportunity above "
            "the configured threshold."
        )

    for opportunity in opportunities:

        print(
            "-" * 70
        )

        print(
            f"Pair:          "
            f"{opportunity.token0} / "
            f"{opportunity.token1}"
        )

        print(
            f"Buy pool:      "
            f"{opportunity.buy_pool}"
        )

        print(
            f"Sell pool:     "
            f"{opportunity.sell_pool}"
        )

        print(
            f"Buy price:     "
            f"{opportunity.buy_price:.12f}"
        )

        print(
            f"Sell price:    "
            f"{opportunity.sell_price:.12f}"
        )

        print(
            f"Spread:        "
            f"{opportunity.gross_spread:.12f}"
        )

        print(
            f"Spread %:      "
            f"{opportunity.gross_spread_percent:.4f}%"
        )

        print(
            f"Gross profit:  "
            f"{opportunity.estimated_profit_per_token0:.12f}"
        )

    print()
    print("=" * 70)
    print(
        "Opportunity detection test complete."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()