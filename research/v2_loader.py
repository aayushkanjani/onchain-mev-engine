from src.amm.pool import AMMPool

from src.blockchain.uniswap_v2 import (
    UniswapV2Factory,
    UniswapV2Pool,
    WETH_ADDRESS,
    USDC_ADDRESS,
)


USDC_DECIMALS = 6
WETH_DECIMALS = 18


def load_v2_pool(client) -> AMMPool:

    factory = UniswapV2Factory(client.w3)

    address = factory.get_pair(
        WETH_ADDRESS,
        USDC_ADDRESS,
    )

    pool = UniswapV2Pool(
        client.w3,
        address,
    )

    token0 = pool.token0()
    reserves = pool.reserves()

    if token0.lower() == USDC_ADDRESS.lower():

        usdc = (
            reserves["reserve0"]
            / 10**USDC_DECIMALS
        )

        weth = (
            reserves["reserve1"]
            / 10**WETH_DECIMALS
        )

    else:

        weth = (
            reserves["reserve0"]
            / 10**WETH_DECIMALS
        )

        usdc = (
            reserves["reserve1"]
            / 10**USDC_DECIMALS
        )

    return AMMPool(
        token_x=USDC_ADDRESS,
        token_y=WETH_ADDRESS,
        reserve_x=usdc,
        reserve_y=weth,
        fee_rate=0.003,
    )