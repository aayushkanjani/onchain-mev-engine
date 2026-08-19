from src.blockchain.client import EthereumClient

from src.blockchain.uniswap_v3 import (
    UniswapV3Factory,
    UniswapV3Pool,
)

from src.blockchain.uniswap_v2 import (
    WETH_ADDRESS,
    USDC_ADDRESS,
)


V3_FEE = 500


def main():

    client = EthereumClient()

    factory = UniswapV3Factory(
        client.w3
    )

    address = factory.get_pool(
        WETH_ADDRESS,
        USDC_ADDRESS,
        V3_FEE,
    )

    pool = UniswapV3Pool(
        client.w3,
        address,
    )

    slot0 = pool.slot0()

    print("=" * 60)
    print("REAL UNISWAP V3 STATE")
    print("=" * 60)

    print(f"\nPool: {address}")

    print("\nSTATE")
    print("-" * 60)

    print(
        f"sqrtPriceX96: {slot0[0]}"
    )

    print(
        f"tick:         {slot0[1]}"
    )

    print(
        f"liquidity:    {pool.liquidity()}"
    )

    print(
        f"fee:          {pool.fee()}"
    )

    print(
        f"tick spacing: {pool.tick_spacing()}"
    )


if __name__ == "__main__":
    main()