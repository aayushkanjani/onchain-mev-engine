from src.amm.arbitrage import simulate_v2_to_v3
from src.amm.pool import AMMPool
from src.amm.v3.pool import V3Pool


def main():

    # ---------------------------------------------------------
    # For now these are controlled parameters.
    # We will replace them with live on-chain state.
    # ---------------------------------------------------------

    v2 = AMMPool(
        token_x="USDC",
        token_y="WETH",
        reserve_x=8_869_721.85,
        reserve_y=4_635.643345,
        fee_rate=0.003,
    )

    # IMPORTANT:
    # This is only a placeholder V3 state.
    # The next step will construct this from Ethereum.
    v3 = V3Pool(
        token0="USDC",
        token1="WETH",
        sqrt_price_x96=1603816224779678239784609882661162,
        tick=198321,
        liquidity=3574022328578472107,
        fee=500,
        tick_spacing=10,
    )

    amounts = [
        100,
        1_000,
        5_000,
        10_000,
        25_000,
    ]

    print("=" * 60)
    print("EXECUTION-AWARE V2 → V3 ARBITRAGE")
    print("=" * 60)

    print("\nASSUMED EXECUTION COST")
    print("-" * 60)
    print("Gas used:       250,000")
    print("Gas price:      20 Gwei")
    print("ETH price:      $2,500")

    print("\nRESULTS")
    print("-" * 60)

    for amount in amounts:

        result = simulate_v2_to_v3(
            amount_in=amount,
            v2_pool=v2,
            v3_pool=v3,
            usdc_token="USDC",
            weth_token="WETH",
            gas_used=250_000,
            gas_price_gwei=20,
            eth_price=2_500,
        )

        status = (
            "PROFITABLE"
            if result.profitable
            else "NO ARBITRAGE"
        )

        print(
            f"${amount:>7,.0f}"
            f" | gross: ${result.gross_profit:>9,.2f}"
            f" | gas: ${result.gas_cost:>7,.2f}"
            f" | net: ${result.net_profit:>9,.2f}"
            f" | {status}"
        )


if __name__ == "__main__":
    main()