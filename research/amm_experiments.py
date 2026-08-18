from src.amm.pool import AMMPool
from src.amm.optimizer import find_optimal_trade_size


def main():

    pool_a = AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100,
        reserve_y=300_000,
    )

    pool_b = AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100,
        reserve_y=302_000,
    )

    print("========== MARKET ==========")

    print(f"Pool A: ${pool_a.spot_price_x_in_y:.2f}")
    print(f"Pool B: ${pool_b.spot_price_x_in_y:.2f}")

    print("\n========== OPTIMIZATION ==========")

    result = find_optimal_trade_size(
        buy_pool=pool_a,
        sell_pool=pool_b,
        min_amount=100,
        max_amount=50_000,
        steps=500,
    )

    if result is None:
        print("No result.")
        return

    print(f"Optimal trade: ${result.amount_in:.2f}")
    print(f"ETH received:  {result.intermediate_amount:.8f}")
    print(f"Final USDC:    ${result.final_amount:.2f}")
    print(f"Profit:        ${result.profit:.2f}")
    print(f"Profitable:    {result.profitable}")


if __name__ == "__main__":
    main()