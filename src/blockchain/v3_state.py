from __future__ import annotations

from src.amm.v3.pool import V3Pool
from src.amm.v3.tick import TickInfo

from src.blockchain.uniswap_v3 import (
    UniswapV3Pool,
)


def build_v3_pool(
    onchain_pool: UniswapV3Pool,
) -> V3Pool:

    slot0 = onchain_pool.slot0()

    sqrt_price_x96 = slot0[0]
    tick = slot0[1]

    liquidity = onchain_pool.liquidity()
    fee = onchain_pool.fee()
    tick_spacing = onchain_pool.tick_spacing()

    token0 = onchain_pool.token0()
    token1 = onchain_pool.token1()

    return V3Pool(
        token0=token0,
        token1=token1,
        sqrt_price_x96=sqrt_price_x96,
        tick=tick,
        liquidity=liquidity,
        fee=fee,
        tick_spacing=tick_spacing,

        bitmap_provider=onchain_pool.tick_bitmap,

        tick_provider=_make_tick_provider(
            onchain_pool
        ),
    )


def _make_tick_provider(
    pool: UniswapV3Pool,
):

    def provider(tick: int) -> TickInfo:

        data = pool.ticks(tick)

        liquidity_net = data[1]
        initialized = data[7]

        if not initialized:
            raise ValueError(
                f"Tick {tick} is not initialized"
            )

        return TickInfo(
            tick=tick,
            liquidity_net=liquidity_net,
        )

    return provider