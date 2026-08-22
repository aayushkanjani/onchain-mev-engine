from __future__ import annotations


def calculate_price(
    amount_in: int,
    amount_out: int,
) -> float:
    """
    Effective execution price.

    Returns quote units per input unit.
    """

    if amount_in <= 0:
        raise ValueError("amount_in must be positive")

    if amount_out <= 0:
        raise ValueError("amount_out must be positive")

    return amount_out / amount_in


def minimum_amount_out(
    expected_amount_out: int,
    slippage_bps: int,
) -> int:
    """
    Calculate the minimum acceptable output.

    Example:
        expected = 1000
        slippage = 50 bps (0.5%)

        minimum output = 995
    """

    if expected_amount_out < 0:
        raise ValueError(
            "expected_amount_out must be non-negative"
        )

    if not 0 <= slippage_bps <= 10_000:
        raise ValueError(
            "slippage_bps must be between 0 and 10000"
        )

    return (
        expected_amount_out
        * (10_000 - slippage_bps)
        // 10_000
    )


def slippage_bps(
    expected_price: float,
    execution_price: float,
) -> float:
    """
    Calculate execution slippage in basis points.

    Positive value means execution was worse than expected.
    """

    if expected_price <= 0:
        raise ValueError(
            "expected_price must be positive"
        )

    return (
        (expected_price - execution_price)
        / expected_price
        * 10_000
    )