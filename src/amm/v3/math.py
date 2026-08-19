from __future__ import annotations

Q96 = 1 << 96

MIN_SQRT_RATIO = 4_295_128_739
MAX_SQRT_RATIO = 1_461_446_703_485_210_328_727_305_220_398_882_372_034_287_170_393_422

UINT160_MAX = (1 << 160) - 1


def mul_div(a: int, b: int, denominator: int) -> int:
    if denominator <= 0:
        raise ValueError("denominator must be positive")

    return (a * b) // denominator


def mul_div_rounding_up(
    a: int,
    b: int,
    denominator: int,
) -> int:

    result = mul_div(a, b, denominator)

    if (a * b) % denominator != 0:
        result += 1

    return result


def div_rounding_up(
    numerator: int,
    denominator: int,
) -> int:

    if denominator <= 0:
        raise ValueError("denominator must be positive")

    return (numerator + denominator - 1) // denominator


def get_amount0_delta(
    sqrt_a: int,
    sqrt_b: int,
    liquidity: int,
    round_up: bool,
) -> int:

    if sqrt_a > sqrt_b:
        sqrt_a, sqrt_b = sqrt_b, sqrt_a

    if sqrt_a <= 0:
        raise ValueError("sqrt price must be positive")

    numerator1 = liquidity << 96
    numerator2 = sqrt_b - sqrt_a

    if round_up:
        first = mul_div_rounding_up(
            numerator1,
            numerator2,
            sqrt_b,
        )

        return div_rounding_up(
            first,
            sqrt_a,
        )

    first = mul_div(
        numerator1,
        numerator2,
        sqrt_b,
    )

    return first // sqrt_a


def get_amount1_delta(
    sqrt_a: int,
    sqrt_b: int,
    liquidity: int,
    round_up: bool,
) -> int:

    if sqrt_a > sqrt_b:
        sqrt_a, sqrt_b = sqrt_b, sqrt_a

    delta = sqrt_b - sqrt_a

    if round_up:
        return mul_div_rounding_up(
            liquidity,
            delta,
            Q96,
        )

    return mul_div(
        liquidity,
        delta,
        Q96,
    )


def get_next_sqrt_price_from_amount0_rounding_up(
    sqrt_p: int,
    liquidity: int,
    amount: int,
    add: bool,
) -> int:

    if sqrt_p <= 0 or liquidity <= 0:
        raise ValueError("invalid sqrt price or liquidity")

    if amount == 0:
        return sqrt_p

    numerator1 = liquidity << 96

    if add:

        denominator = numerator1 + amount * sqrt_p

        if denominator >= numerator1:
            return mul_div_rounding_up(
                numerator1,
                sqrt_p,
                denominator,
            )

        # Overflow-safe equivalent.
        return div_rounding_up(
            numerator1,
            (numerator1 // sqrt_p) + amount,
        )

    denominator = numerator1 - amount * sqrt_p

    if denominator <= 0:
        raise ValueError("price calculation underflow")

    return mul_div_rounding_up(
        numerator1,
        sqrt_p,
        denominator,
    )


def get_next_sqrt_price_from_amount1_rounding_down(
    sqrt_p: int,
    liquidity: int,
    amount: int,
    add: bool,
) -> int:

    if liquidity <= 0:
        raise ValueError("liquidity must be positive")

    if add:

        if amount <= UINT160_MAX:
            quotient = (amount << 96) // liquidity
        else:
            quotient = mul_div(
                amount,
                Q96,
                liquidity,
            )

        return sqrt_p + quotient

    if amount <= UINT160_MAX:
        quotient = div_rounding_up(
            amount << 96,
            liquidity,
        )
    else:
        quotient = mul_div_rounding_up(
            amount,
            Q96,
            liquidity,
        )

    if sqrt_p <= quotient:
        raise ValueError("sqrt price underflow")

    return sqrt_p - quotient


def get_next_sqrt_price_from_input(
    sqrt_p: int,
    liquidity: int,
    amount_in: int,
    zero_for_one: bool,
) -> int:

    if sqrt_p <= 0:
        raise ValueError("invalid sqrt price")

    if liquidity <= 0:
        raise ValueError("invalid liquidity")

    if zero_for_one:

        return get_next_sqrt_price_from_amount0_rounding_up(
            sqrt_p,
            liquidity,
            amount_in,
            True,
        )

    return get_next_sqrt_price_from_amount1_rounding_down(
        sqrt_p,
        liquidity,
        amount_in,
        True,
    )


def get_next_sqrt_price_from_output(
    sqrt_p: int,
    liquidity: int,
    amount_out: int,
    zero_for_one: bool,
) -> int:

    if sqrt_p <= 0:
        raise ValueError("invalid sqrt price")

    if liquidity <= 0:
        raise ValueError("invalid liquidity")

    if zero_for_one:

        return get_next_sqrt_price_from_amount1_rounding_down(
            sqrt_p,
            liquidity,
            amount_out,
            False,
        )

    return get_next_sqrt_price_from_amount0_rounding_up(
        sqrt_p,
        liquidity,
        amount_out,
        False,
    )