from src.amm.v3.tick import (
    MIN_TICK,
    MAX_TICK,
    compress_tick,
    position,
    get_sqrt_ratio_at_tick,
    get_tick_at_sqrt_ratio,
)


def test_tick_round_trip():

    ticks = [
        -887000,
        -100000,
        -10,
        0,
        10,
        100000,
        200753,
        887000,
    ]

    for tick in ticks:

        sqrt_price = (
            get_sqrt_ratio_at_tick(tick)
        )

        recovered = (
            get_tick_at_sqrt_ratio(
                sqrt_price
            )
        )

        assert recovered == tick


def test_tick_bitmap_position():

    assert position(0) == (0, 0)

    assert position(1) == (0, 1)

    assert position(255) == (0, 255)

    assert position(256) == (1, 0)


def test_negative_bitmap_position():

    word, bit = position(-1)

    assert word == -1
    assert bit == 255


def test_compress_tick():

    assert compress_tick(0, 10) == 0
    assert compress_tick(10, 10) == 1
    assert compress_tick(19, 10) == 1
    assert compress_tick(-1, 10) == -1
    assert compress_tick(-10, 10) == -1