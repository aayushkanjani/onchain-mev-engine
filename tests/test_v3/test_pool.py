from src.amm.v3.pool import V3Pool
from src.amm.v3.tick import TickInfo


def make_pool():

    return V3Pool(
        token0="USDC",
        token1="WETH",
        sqrt_price_x96=1 << 96,
        tick=0,
        liquidity=1_000_000,
        fee=500,
        tick_spacing=10,
        initialized_ticks=[
            TickInfo(
                tick=-100,
                liquidity_net=500_000,
            ),
            TickInfo(
                tick=100,
                liquidity_net=-300_000,
            ),
        ],
    )


def test_swap_exact_input():

    pool = make_pool()

    result = pool.swap_exact_input(
        amount_in=1_000,
        zero_for_one=True,
    )

    assert result.amount_in > 0
    assert result.amount_out > 0
    assert result.fee_amount > 0


def test_swap_moves_price():

    pool = make_pool()

    before = pool.sqrt_price_x96

    result = pool.swap_exact_input(
        amount_in=1_000,
        zero_for_one=True,
    )

    assert result.sqrt_price_after < before


def test_tick_crossing_is_reported():

    pool = make_pool()

    result = pool.swap_exact_input(
        amount_in=10_000_000,
        zero_for_one=True,
    )

    assert result.amount_out > 0
    assert len(result.ticks_crossed) >= 1