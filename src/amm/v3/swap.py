from dataclasses import dataclass

from .math import (
    get_amount0_delta,
    get_amount1_delta,
    get_next_sqrt_price_from_input,
    get_next_sqrt_price_from_output,
    mul_div,
    mul_div_rounding_up,
)


FEE_DENOMINATOR = 1_000_000


@dataclass
class SwapStepResult:

    sqrt_price_next: int

    amount_in: int
    amount_out: int
    fee_amount: int


def compute_swap_step(
    sqrt_price_current: int,
    sqrt_price_target: int,
    liquidity: int,
    amount_remaining: int,
    fee_pips: int,
) -> SwapStepResult:

    if liquidity <= 0:
        raise ValueError("liquidity must be positive")

    if fee_pips < 0 or fee_pips >= FEE_DENOMINATOR:
        raise ValueError("invalid fee")

    zero_for_one = (
        sqrt_price_current >= sqrt_price_target
    )

    exact_input = amount_remaining >= 0

    if exact_input:

        amount_remaining_less_fee = mul_div(
            amount_remaining,
            FEE_DENOMINATOR - fee_pips,
            FEE_DENOMINATOR,
        )

        if zero_for_one:

            amount_in_to_target = get_amount0_delta(
                sqrt_price_target,
                sqrt_price_current,
                liquidity,
                True,
            )

        else:

            amount_in_to_target = get_amount1_delta(
                sqrt_price_current,
                sqrt_price_target,
                liquidity,
                True,
            )

        if (
            amount_remaining_less_fee
            >= amount_in_to_target
        ):

            sqrt_price_next = sqrt_price_target

        else:

            sqrt_price_next = (
                get_next_sqrt_price_from_input(
                    sqrt_price_current,
                    liquidity,
                    amount_remaining_less_fee,
                    zero_for_one,
                )
            )

    else:

        amount_remaining_out = -amount_remaining

        if zero_for_one:

            amount_out_to_target = get_amount1_delta(
                sqrt_price_target,
                sqrt_price_current,
                liquidity,
                False,
            )

        else:

            amount_out_to_target = get_amount0_delta(
                sqrt_price_current,
                sqrt_price_target,
                liquidity,
                False,
            )

        if (
            amount_remaining_out
            >= amount_out_to_target
        ):

            sqrt_price_next = sqrt_price_target

        else:

            sqrt_price_next = (
                get_next_sqrt_price_from_output(
                    sqrt_price_current,
                    liquidity,
                    amount_remaining_out,
                    zero_for_one,
                )
            )

    max_reached = (
        sqrt_price_next == sqrt_price_target
    )

    if zero_for_one:

        if max_reached and exact_input:

            amount_in = get_amount0_delta(
                sqrt_price_target,
                sqrt_price_current,
                liquidity,
                True,
            )

        else:

            amount_in = get_amount0_delta(
                sqrt_price_next,
                sqrt_price_current,
                liquidity,
                True,
            )

        if max_reached and not exact_input:

            amount_out = get_amount1_delta(
                sqrt_price_target,
                sqrt_price_current,
                liquidity,
                False,
            )

        else:

            amount_out = get_amount1_delta(
                sqrt_price_next,
                sqrt_price_current,
                liquidity,
                False,
            )

    else:

        if max_reached and exact_input:

            amount_in = get_amount1_delta(
                sqrt_price_current,
                sqrt_price_target,
                liquidity,
                True,
            )

        else:

            amount_in = get_amount1_delta(
                sqrt_price_current,
                sqrt_price_next,
                liquidity,
                True,
            )

        if max_reached and not exact_input:

            amount_out = get_amount0_delta(
                sqrt_price_current,
                sqrt_price_target,
                liquidity,
                False,
            )

        else:

            amount_out = get_amount0_delta(
                sqrt_price_current,
                sqrt_price_next,
                liquidity,
                False,
            )

    if not exact_input:

        amount_out = min(
            amount_out,
            -amount_remaining,
        )

    if (
        exact_input
        and sqrt_price_next != sqrt_price_target
    ):

        fee_amount = (
            amount_remaining
            - amount_in
        )

    else:

        fee_amount = mul_div_rounding_up(
            amount_in,
            fee_pips,
            FEE_DENOMINATOR - fee_pips,
        )

    return SwapStepResult(
        sqrt_price_next=sqrt_price_next,
        amount_in=amount_in,
        amount_out=amount_out,
        fee_amount=fee_amount,
    )