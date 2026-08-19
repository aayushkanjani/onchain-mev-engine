from dataclasses import dataclass

from src.amm.arbitrage import simulate_arbitrage


@dataclass
class OptimizationResult:
    amount_in: float
    profit: float


def grid_search(
    profit_function,
    min_amount: float,
    max_amount: float,
    steps: int = 100,
) -> OptimizationResult:
    """
    Generic grid-search optimizer.

    Evaluates the profit function at several trade sizes
    and returns the most profitable one.
    """

    if steps <= 0:
        raise ValueError("steps must be positive")

    if min_amount < 0:
        raise ValueError(
            "min_amount must be non-negative"
        )

    if max_amount <= min_amount:
        raise ValueError(
            "max_amount must be greater than min_amount"
        )

    step_size = (
        max_amount - min_amount
    ) / steps

    best_amount = min_amount
    best_profit = profit_function(min_amount)

    for i in range(1, steps + 1):

        amount = (
            min_amount
            + i * step_size
        )

        profit = profit_function(amount)

        if profit > best_profit:

            best_profit = profit
            best_amount = amount

    return OptimizationResult(
        amount_in=best_amount,
        profit=best_profit,
    )


def find_optimal_trade_size(
    buy_pool,
    sell_pool,
    min_amount: float,
    max_amount: float,
    steps: int = 100,
):
    """
    Find the optimal arbitrage trade size between
    two constant-product AMMs.

    buy_pool:
        Pool where we buy the intermediate asset.

    sell_pool:
        Pool where we sell the intermediate asset.

    The trade is simulated for different input sizes
    and the size with the highest PnL is returned.

    For backwards compatibility, this function returns
    the OptimizationResult object expected by the tests.
    """

    def profit_function(amount_in: float) -> float:

        result = simulate_arbitrage(
            buy_pool=buy_pool,
            sell_pool=sell_pool,
            amount_in=amount_in,
        )

        return result.profit

    return grid_search(
        profit_function=profit_function,
        min_amount=min_amount,
        max_amount=max_amount,
        steps=steps,
    )