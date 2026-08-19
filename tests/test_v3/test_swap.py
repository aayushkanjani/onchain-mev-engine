from src.amm.v3.swap import (
    compute_swap_step,
)

from src.amm.v3.math import Q96


def test_swap_step_token1():

    liquidity = 1_000_000

    current = Q96
    target = 2 * Q96

    result = compute_swap_step(
        sqrt_price_current=current,
        sqrt_price_target=target,
        liquidity=liquidity,
        amount_remaining=10_000,
        fee_pips=500,
    )

    assert result.amount_in > 0
    assert result.amount_out > 0
    assert result.fee_amount > 0

    assert result.sqrt_price_next > current