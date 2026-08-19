from src.amm.v3.math import (
    Q96,
    get_amount0_delta,
    get_amount1_delta,
)


def test_q96():

    assert Q96 == 2**96


def test_amount1_delta():

    liquidity = 1_000_000

    sqrt_a = Q96
    sqrt_b = 2 * Q96

    result = get_amount1_delta(
        sqrt_a,
        sqrt_b,
        liquidity,
        False,
    )

    assert result == 1_000_000


def test_amount0_delta():

    liquidity = 1_000_000

    sqrt_a = Q96
    sqrt_b = 2 * Q96

    result = get_amount0_delta(
        sqrt_a,
        sqrt_b,
        liquidity,
        False,
    )

    assert result == 500_000