from src.amm.pool import AMMPool
from src.amm.arbitrage import simulate_arbitrage


def main():

    # Pool A: ETH is cheaper
    pool_a = AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100,
        reserve_y=300_000,
    )

    # Pool B: ETH is more expensive
    pool_b = AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100,
        reserve_y=305_000,
    )

    print("========== MARKET ==========")

    print(f"Pool A ETH price: ${pool_a.spot_price_x_in_y:.2f}")
    print(f"Pool B ETH price: ${pool_b.spot_price_x_in_y:.2f}")

    print("\n========== ARBITRAGE ==========")

    for amount_in in [100, 1_000, 5_000, 10_000, 25_000, 50_000]:

        result = simulate_arbitrage(
            buy_pool=pool_a,
            sell_pool=pool_b,
            amount_in=amount_in,
        )

        print(
            f"${amount_in:>7,.0f} → "
            f"${result.final_amount:>10,.2f} | "
            f"PnL: ${result.profit:>8,.2f} | "
            f"Profitable: {result.profitable}"
        )


if __name__ == "__main__":
    main()