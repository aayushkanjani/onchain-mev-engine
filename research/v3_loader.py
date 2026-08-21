from __future__ import annotations

from src.amm.v3.pool import V3Pool, InitializedTick
from src.blockchain.uniswap_v3 import (
    UniswapV3Factory,
    UniswapV3Pool,
)

from src.blockchain.uniswap_v2 import (
    WETH_ADDRESS,
    USDC_ADDRESS,
)


V3_FEE = 500


def load_v3_pool(client) -> V3Pool:

    factory = UniswapV3Factory(client.w3)

    address = factory.get_pool(
        WETH_ADDRESS,
        USDC_ADDRESS,
        V3_FEE,
    )

    chain_pool = UniswapV3Pool(
        client.w3,
        address,
    )

    slot0 = chain_pool.slot0()

    sqrt_price_x96 = slot0[0]
    tick = slot0[1]

    liquidity = chain_pool.liquidity()
    fee = chain_pool.fee()
    tick_spacing = chain_pool.tick_spacing()

    token0 = chain_pool.token0()
    token1 = chain_pool.token1()

    return V3Pool(
        token0=token0,
        token1=token1,
        sqrt_price_x96=sqrt_price_x96,
        tick=tick,
        liquidity=liquidity,
        fee=fee,
        tick_spacing=tick_spacing,
        initialized_ticks=[],
    )