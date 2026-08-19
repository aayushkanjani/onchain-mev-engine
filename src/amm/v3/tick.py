import math

from .math import Q96


MIN_TICK = -887272
MAX_TICK = 887272

MIN_SQRT_RATIO = 4_295_128_739

MAX_SQRT_RATIO = (
    1_461_446_703_485_210_328_727_305_220_398_882_372_034_287_170_393_422
)


def get_sqrt_ratio_at_tick(tick: int) -> int:

    if tick < MIN_TICK or tick > MAX_TICK:
        raise ValueError(
            f"tick {tick} outside [{MIN_TICK}, {MAX_TICK}]"
        )

    # Mathematical definition:
    #
    # sqrtPrice = sqrt(1.0001 ** tick)
    #
    # V3 stores this as Q64.96.

    value = math.sqrt(
        1.0001 ** tick
    )

    return int(value * Q96)


def get_tick_at_sqrt_ratio(
    sqrt_price_x96: int,
) -> int:

    if not (
        MIN_SQRT_RATIO
        <= sqrt_price_x96
        < MAX_SQRT_RATIO
    ):
        raise ValueError(
            "sqrt price outside valid V3 range"
        )

    price = (
        sqrt_price_x96 / Q96
    ) ** 2

    tick = math.floor(
        math.log(price) / math.log(1.0001)
    )

    # Correct floating-point boundary errors.
    while (
        tick < MAX_TICK
        and get_sqrt_ratio_at_tick(tick + 1)
        <= sqrt_price_x96
    ):
        tick += 1

    while (
        tick > MIN_TICK
        and get_sqrt_ratio_at_tick(tick)
        > sqrt_price_x96
    ):
        tick -= 1

    return tick