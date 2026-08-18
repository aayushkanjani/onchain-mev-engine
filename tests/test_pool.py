import pytest

from src.amm.pool import AMMPool


def create_pool():
    return AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100,
        reserve_y=300_000,
        fee_rate=0.003,
    )


def test_initial_spot_price():

    pool = create_pool()

    assert pool.spot_price_x_in_y == 3000


def test_fee_calculation():

    pool = create_pool()

    fee = pool.calculate_fee(3000)

    assert fee == pytest.approx(9.0)


def test_amount_after_fee():

    pool = create_pool()

    amount_in = 3000
    fee = pool.calculate_fee(amount_in)

    amount_after_fee = amount_in - fee

    assert amount_after_fee == pytest.approx(2991.0)


def test_swap_returns_output():

    pool = create_pool()

    eth_out = pool.get_amount_out(
        amount_in=3000,
        token_in="USDC",
    )

    assert eth_out > 0
    assert eth_out < 1


def test_swap_changes_reserves():

    pool = create_pool()

    initial_eth = pool.reserve_x
    initial_usdc = pool.reserve_y

    pool.swap(
        amount_in=3000,
        token_in="USDC",
    )

    # Trader bought ETH.
    assert pool.reserve_x < initial_eth

    # Trader sent USDC.
    assert pool.reserve_y > initial_usdc


def test_swap_preserves_positive_reserves():

    pool = create_pool()

    pool.swap(
        amount_in=3000,
        token_in="USDC",
    )

    assert pool.reserve_x > 0
    assert pool.reserve_y > 0


def test_invalid_token():

    pool = create_pool()

    with pytest.raises(ValueError):

        pool.get_amount_out(
            amount_in=100,
            token_in="BTC",
        )


def test_invalid_amount():

    pool = create_pool()

    with pytest.raises(ValueError):

        pool.get_amount_out(
            amount_in=0,
            token_in="USDC",
        )