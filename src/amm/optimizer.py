from src.amm.arbitrage import ArbitrageResult, simulate_arbitrage
from src.amm.pool import AMMPool


def find_optimal_trade_size(
    buy_pool: AMMPool,
    sell_pool: AMMPool,
    min_amount: float,
    max_amount: float,
    steps: int = 100,
) -> ArbitrageResult | None:
    """
    Search for the trade size that maximizes arbitrage profit.

    This is intentionally a simple grid search.
    Later we can replace it with a mathematical optimizer.
    """

    if min_amount <= 0:
        raise ValueError("min_amount must be positive")

    if max_amount <= min_amount:
        raise ValueError("max_amount must be greater than min_amount")

    best_result = None

    step_size = (max_amount - min_amount) / steps

    for i in range(steps + 1):

        amount = min_amount + i * step_size

        result = simulate_arbitrage(
            buy_pool=buy_pool,
            sell_pool=sell_pool,
            amount_in=amount,
        )

        if best_result is None or result.profit > best_result.profit:
            best_result = result

    return best_result