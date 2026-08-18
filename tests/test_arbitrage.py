import pytest

from src.amm.pool import AMMPool
from src.amm.arbitrage import simulate_arbitrage
from src.amm.optimizer import find_optimal_trade_size


def create_pools():

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

    return pool_a, pool_b


def test_arbitrage_simulation():

    pool_a, pool_b = create_pools()

    result = simulate_arbitrage(
        buy_pool=pool_a,
        sell_pool=pool_b,
        amount_in=100,
    )

    assert result.intermediate_amount > 0
    assert result.final_amount > 0


def test_simulation_does_not_modify_pools():

    pool_a, pool_b = create_pools()

    original_a = (pool_a.reserve_x, pool_a.reserve_y)
    original_b = (pool_b.reserve_x, pool_b.reserve_y)

    simulate_arbitrage(
        buy_pool=pool_a,
        sell_pool=pool_b,
        amount_in=1000,
    )

    assert (pool_a.reserve_x, pool_a.reserve_y) == original_a
    assert (pool_b.reserve_x, pool_b.reserve_y) == original_b


def test_unprofitable_opportunity():
    
    pool_a, pool_b = create_pools()

    result = simulate_arbitrage(
        buy_pool=pool_a,
        sell_pool=pool_b,
        amount_in=100,
    )

    assert result.profit < 0
    assert not result.profitable


def test_optimizer_returns_result():

    pool_a, pool_b = create_pools()

    result = find_optimal_trade_size(
        buy_pool=pool_a,
        sell_pool=pool_b,
        min_amount=100,
        max_amount=10_000,
        steps=100,
    )

    assert result is not None
    assert result.amount_in >= 100
    assert result.amount_in <= 10_000