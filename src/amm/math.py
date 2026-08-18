def calculate_amount_out(
    reserve_in: float,
    reserve_out: float,
    amount_in: float,
    fee_rate: float = 0.003,
) -> float:
    """
    Calculate the output amount for a constant-product AMM.

    This function does not modify any state.
    """

    if reserve_in <= 0:
        raise ValueError("reserve_in must be positive")

    if reserve_out <= 0:
        raise ValueError("reserve_out must be positive")

    if amount_in <= 0:
        raise ValueError("amount_in must be positive")

    if not 0 <= fee_rate < 1:
        raise ValueError("fee_rate must be between 0 and 1")

    # Trading fee
    fee = amount_in * fee_rate

    # Amount actually used by the AMM formula
    amount_in_after_fee = amount_in - fee

    # Constant-product AMM formula
    amount_out = (
        reserve_out * amount_in_after_fee
        / (reserve_in + amount_in_after_fee)
    )

    return amount_out