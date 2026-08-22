from src.amm.slippage import (
    minimum_amount_out,
    slippage_bps,
)


def test_minimum_amount_out():

    assert minimum_amount_out(
        expected_amount_out=100_000,
        slippage_bps=50,
    ) == 99_500


def test_zero_slippage():

    assert minimum_amount_out(
        expected_amount_out=100_000,
        slippage_bps=0,
    ) == 100_000


def test_slippage_calculation():

    result = slippage_bps(
        expected_price=100,
        execution_price=99.5,
    )

    assert abs(result - 50) < 1e-9