from src.blockchain.client import EthereumClient
from src.blockchain.uniswap_v2 import (
    UniswapV2Factory,
    UniswapV2Pool,
    WETH_ADDRESS,
    USDC_ADDRESS,
)


WETH_DECIMALS = 18
USDC_DECIMALS = 6


def main():

    client = EthereumClient()

    factory = UniswapV2Factory(client.w3)

    pair_address = factory.get_pair(
        WETH_ADDRESS,
        USDC_ADDRESS,
    )

    print("=" * 60)
    print("UNISWAP V2")
    print("=" * 60)

    print(f"WETH: {WETH_ADDRESS}")
    print(f"USDC: {USDC_ADDRESS}")
    print(f"Pair: {pair_address}")

    pool = UniswapV2Pool(
        client.w3,
        pair_address,
    )

    token0 = pool.token0()
    token1 = pool.token1()

    reserves = pool.reserves()

    print("\nTOKENS")
    print("-" * 60)

    print(f"Token0: {token0}")
    print(f"Token1: {token1}")

    print("\nRAW RESERVES")
    print("-" * 60)

    print(f"Reserve0: {reserves['reserve0']}")
    print(f"Reserve1: {reserves['reserve1']}")

    print("\nHUMAN RESERVES")
    print("-" * 60)

    if token0.lower() == WETH_ADDRESS.lower():

        weth_raw = reserves["reserve0"]
        usdc_raw = reserves["reserve1"]

    else:

        weth_raw = reserves["reserve1"]
        usdc_raw = reserves["reserve0"]

    weth = weth_raw / 10**WETH_DECIMALS
    usdc = usdc_raw / 10**USDC_DECIMALS

    print(f"WETH: {weth:,.6f}")
    print(f"USDC: {usdc:,.2f}")

    price = usdc / weth

    print("\nMARKET")
    print("-" * 60)

    print(f"WETH/USDC price: ${price:,.2f}")

    print(f"\nLast reserve update timestamp:")
    print(reserves["timestamp"])


if __name__ == "__main__":
    main()