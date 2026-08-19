from src.blockchain.client import EthereumClient

from src.blockchain.uniswap_v2 import (
    UniswapV2Factory,
    UniswapV2Pool,
    WETH_ADDRESS,
    USDC_ADDRESS,
)

from src.blockchain.uniswap_v3 import (
    UniswapV3Factory,
    UniswapV3Pool,
)


USDC_DECIMALS = 6
WETH_DECIMALS = 18

V3_FEE = 500


def v3_price_from_sqrt_price(
    sqrt_price_x96: int,
    token0: str,
    token1: str,
) -> float:

    # sqrtPriceX96 represents:
    #
    # sqrt(token1_raw / token0_raw) * 2^96
    #
    # Therefore:
    #
    # token1_raw / token0_raw
    #
    raw_price = (
        sqrt_price_x96 / 2**96
    ) ** 2

    # Convert raw token units into human-readable units.
    #
    # human_price =
    # raw_price * 10^(decimals_token0 - decimals_token1)

    if token0.lower() == USDC_ADDRESS.lower():

        # token0 = USDC, 6 decimals
        # token1 = WETH, 18 decimals
        #
        # raw price = WETH_raw / USDC_raw
        #
        # We want:
        # USDC / WETH

        human_weth_per_usdc = (
            raw_price
            * 10 ** (
                USDC_DECIMALS - WETH_DECIMALS
            )
        )

        return 1 / human_weth_per_usdc

    elif token0.lower() == WETH_ADDRESS.lower():

        # token0 = WETH
        # token1 = USDC
        #
        # raw price = USDC_raw / WETH_raw
        #
        # Convert to human USDC/WETH.

        return (
            raw_price
            * 10 ** (
                WETH_DECIMALS - USDC_DECIMALS
            )
        )

    else:

        raise ValueError(
            "Unexpected token configuration"
        )


def main():

    client = EthereumClient()

    # ==================================================
    # UNISWAP V2
    # ==================================================

    v2_factory = UniswapV2Factory(
        client.w3
    )

    v2_address = v2_factory.get_pair(
        WETH_ADDRESS,
        USDC_ADDRESS,
    )

    v2_pool = UniswapV2Pool(
        client.w3,
        v2_address,
    )

    v2_token0 = v2_pool.token0()

    v2_reserves = v2_pool.reserves()

    if v2_token0.lower() == USDC_ADDRESS.lower():

        usdc = (
            v2_reserves["reserve0"]
            / 10**USDC_DECIMALS
        )

        weth = (
            v2_reserves["reserve1"]
            / 10**WETH_DECIMALS
        )

    else:

        weth = (
            v2_reserves["reserve0"]
            / 10**WETH_DECIMALS
        )

        usdc = (
            v2_reserves["reserve1"]
            / 10**USDC_DECIMALS
        )

    v2_price = usdc / weth

    # ==================================================
    # UNISWAP V3
    # ==================================================

    v3_factory = UniswapV3Factory(
        client.w3
    )

    v3_address = v3_factory.get_pool(
        WETH_ADDRESS,
        USDC_ADDRESS,
        V3_FEE,
    )

    if int(v3_address, 16) == 0:

        raise RuntimeError(
            "Uniswap V3 pool does not exist"
        )

    v3_pool = UniswapV3Pool(
        client.w3,
        v3_address,
    )

    v3_token0 = v3_pool.token0()
    v3_token1 = v3_pool.token1()

    slot0 = v3_pool.slot0()

    sqrt_price_x96 = slot0[0]
    tick = slot0[1]

    v3_price = v3_price_from_sqrt_price(
        sqrt_price_x96,
        v3_token0,
        v3_token1,
    )

    # ==================================================
    # OUTPUT
    # ==================================================

    print("=" * 60)
    print("REAL UNISWAP V2 vs V3")
    print("=" * 60)

    print("\nV2")
    print("-" * 60)

    print(f"Pool:  {v2_address}")
    print(f"Price: ${v2_price:,.2f}")

    print("\nV3")
    print("-" * 60)

    print(f"Pool:  {v3_address}")
    print(f"Fee:   {V3_FEE / 1_000_000:.2%}")
    print(f"Tick:  {tick}")
    print(f"Price: ${v3_price:,.2f}")

    print("\nPRICE DIFFERENCE")
    print("-" * 60)

    difference = v3_price - v2_price

    percentage = (
        difference / v2_price
    ) * 100

    print(f"Absolute: ${difference:,.2f}")
    print(f"Relative: {percentage:.4f}%")


if __name__ == "__main__":
    main()