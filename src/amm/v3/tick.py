from __future__ import annotations

from dataclasses import dataclass

from .math import Q96


MIN_TICK = -887272
MAX_TICK = 887272

MIN_SQRT_RATIO = 4_295_128_739

MAX_SQRT_RATIO = (
    1_461_446_703_485_210_328_727_305_220_398_882_372_034_287_170_393_422
)


_TICK_RATIO_CONSTANTS = (
    0xFFFcb933BD6fad37aa2d162D1A594001,
    0xFFF97272373D413259A46990580E213A,
    0xFFF2E50F5F656932EF12357CF3C7FDCC,
    0xFFE5CACA7E10E4E61C3624EAA0941CD0,
    0xFFCB9843D60F6159C9DB58835C926644,
    0xFF973B41FA98C081472E6896DFB254C0,
    0xFF2EA16466C96A3843EC78B326B52861,
    0xFE5DEE046A99A2A811C461F1969C3053,
    0xFCBE86C7900A88AEDCFFC83B479AA3A4,
    0xF987A7253AC413176F2B074CF7815E54,
    0xF3392B0822B70005940C7A398E4B70F3,
    0xE7159475A2C29B7443B29C7FA6E889D9,
    0xD097F3BDFD2022B8845AD8F792AA5825,
    0xA9F746462D870FDF8A65DC1F90E061E5,
    0x70D869A156D2A1B890BB3DF62BAF32F7,
    0x31BE135F97D08FD981231505542FCFA6,
    0x9AA508B5B7A84E1C677DE54F3E99BC9,
    0x5D6AF8DEDB81196699C329225EE604,
    0x2216E584F5FA1EA926041BEDFE98,
    0x48A170391F7DC42444E8FA2,
)


def get_sqrt_ratio_at_tick(tick: int) -> int:

    if tick < MIN_TICK or tick > MAX_TICK:
        raise ValueError(
            f"tick {tick} outside [{MIN_TICK}, {MAX_TICK}]"
        )

    abs_tick = -tick if tick < 0 else tick

    ratio = (
        _TICK_RATIO_CONSTANTS[0]
        if abs_tick & 1
        else 0x100000000000000000000000000000000
    )

    for i in range(1, len(_TICK_RATIO_CONSTANTS)):

        if abs_tick & (1 << i):

            ratio = (
                ratio
                * _TICK_RATIO_CONSTANTS[i]
            ) >> 128

    if tick > 0:

        ratio = (
            ((1 << 256) - 1)
            // ratio
        )

    sqrt_price_x96 = ratio >> 32

    if ratio & ((1 << 32) - 1):

        sqrt_price_x96 += 1

    return sqrt_price_x96


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

    import math

    price = sqrt_price_x96 / Q96

    tick = math.floor(
        math.log(price * price)
        / math.log(1.0001)
    )

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


def compress_tick(
    tick: int,
    tick_spacing: int,
) -> int:

    if tick_spacing <= 0:
        raise ValueError(
            "tick_spacing must be positive"
        )

    return tick // tick_spacing


@dataclass(frozen=True)
class TickInfo:
    """
    Minimal tick information required by
    the V3 swap engine.
    """

    tick: int
    liquidity_net: int


def tick_info_from_chain(
    tick: int,
    raw_tick_data: tuple,
) -> TickInfo:
    """
    Convert the raw result of Uniswap V3's
    ticks() call into TickInfo.

    ticks() returns:

        liquidityGross
        liquidityNet
        feeGrowthOutside0X128
        feeGrowthOutside1X128
        tickCumulativeOutside
        secondsPerLiquidityOutsideX128
        secondsOutside
        initialized

    The swap engine only needs liquidityNet.
    """

    if len(raw_tick_data) < 2:
        raise ValueError(
            "Invalid Uniswap V3 tick data"
        )

    return TickInfo(
        tick=tick,
        liquidity_net=int(
            raw_tick_data[1]
        ),
    )


def position(
    compressed_tick: int,
) -> tuple[int, int]:

    word_position = compressed_tick >> 8

    bit_position = (
        compressed_tick & 255
    )

    return (
        word_position,
        bit_position,
    )


def is_initialized(
    bitmap_word: int,
    bit_position: int,
) -> bool:

    return (
        bitmap_word
        & (1 << bit_position)
    ) != 0