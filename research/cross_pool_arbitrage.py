from __future__ import annotations

from src.blockchain.client import EthereumClient

from src.blockchain.uniswap_v2 import (
    WETH_ADDRESS,
    USDC_ADDRESS,
)

from src.amm.v3.arbitrage import (
    simulate_v2_to_v3,
)

from src.amm.optimizer import grid_search

from research.v2_loader import load_v2_pool
from research.v3_loader import load_v3_pool


USDC_DECIMALS = 6
WETH_DECIMALS = 18


def main():

    client = EthereumClient()

    # ============================================================
    # LOAD REAL POOLS
    # ============================================================

    v2 = load_v2_pool(client)
    v3 = load_v3_pool(client)

    print("=" * 60)
    print("REAL V2 → V3 ARBITRAGE")
    print("=" * 60)

    print(
        f"\nV2 price: "
        f"${v2.spot_price_y_in_x:,.2f}"
    )

    # ------------------------------------------------------------
    # V3 marginal price
    #
    # This is only for displaying the market state.
    # The actual simulation uses swap_exact_input().
    # ------------------------------------------------------------

    sqrt_price = v3.sqrt_price_x96

    raw_price = (
        sqrt_price / 2**96
    ) ** 2

    if v3.token0.lower() == USDC_ADDRESS.lower():

        # token0 = USDC
        # token1 = WETH

        weth_per_usdc = (
            raw_price
            * 10 ** (
                USDC_DECIMALS
                - WETH_DECIMALS
            )
        )

        v3_price = 1 / weth_per_usdc

    else:

        v3_price = (
            raw_price
            * 10 ** (
                WETH_DECIMALS
                - USDC_DECIMALS
            )
        )

    print(
        f"V3 price: "
        f"${v3_price:,.2f}"
    )

    spread = (
        v3_price
        - v2.spot_price_y_in_x
    )

    spread_pct = (
        spread
        / v2.spot_price_y_in_x
        * 100
    )

    print(
        f"Spread: "
        f"${spread:,.2f} "
        f"({spread_pct:.4f}%)"
    )

    # ============================================================
    # TEST TRADE SIZES
    # ============================================================

    print("\nRESULTS")
    print("-" * 60)

    amounts = [
        100,
        1_000,
        5_000,
        10_000,
        25_000,
    ]

    for amount in amounts:

        # Convert human USDC → raw units
        amount_raw = int(
            amount * 10**USDC_DECIMALS
        )

        result = simulate_v2_to_v3(
            amount_in=amount_raw,
            v2_pool=v2,
            v3_pool=v3,
            usdc_token=USDC_ADDRESS,
            weth_token=WETH_ADDRESS,
        )

        received_usdc = (
            result.usdc_received
            / 10**USDC_DECIMALS
        )

        pnl = (
            result.net_profit
            / 10**USDC_DECIMALS
        )

        print(
            f"${amount:>7,.0f}"
            f" → "
            f"${received_usdc:>10,.2f}"
            f" | PnL: "
            f"${pnl:>8,.2f}"
            f" | ticks: "
            f"{len(result.v3_ticks_crossed)}"
        )

    # ============================================================
    # OPTIMIZATION
    # ============================================================

    print("\nOPTIMAL TRADE")
    print("-" * 60)

    def profit_function(amount):

        amount_raw = int(
            amount * 10**USDC_DECIMALS
        )

        result = simulate_v2_to_v3(
            amount_in=amount_raw,
            v2_pool=v2,
            v3_pool=v3,
            usdc_token=USDC_ADDRESS,
            weth_token=WETH_ADDRESS,
        )

        return (
            result.net_profit
            / 10**USDC_DECIMALS
        )

    optimization = grid_search(
        profit_function=profit_function,
        min_amount=1,
        max_amount=25_000,
        steps=100,
    )

    print(
        f"Trade size: "
        f"${optimization.amount_in:,.2f}"
    )

    print(
        f"Maximum PnL: "
        f"${optimization.profit:,.4f}"
    )

    if optimization.profit > 0:

        print("Status: ARBITRAGE")

    else:

        print("Status: NO ARBITRAGE")


if __name__ == "__main__":
    main()