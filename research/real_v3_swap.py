from src.blockchain.client import EthereumClient
from src.blockchain.uniswap_v3 import (
    UniswapV3Factory,
    UniswapV3Pool,
)
from src.blockchain.uniswap_v2 import (
    WETH_ADDRESS,
    USDC_ADDRESS,
)
from src.blockchain.v3_state import build_v3_pool


V3_FEE = 500

WETH_DECIMALS = 18
USDC_DECIMALS = 6


def main():

    print("=" * 60)
    print("REAL ON-CHAIN UNISWAP V3 SWAP")
    print("=" * 60)

    client = EthereumClient()

    factory = UniswapV3Factory(
        client.w3
    )

    pool_address = factory.get_pool(
        WETH_ADDRESS,
        USDC_ADDRESS,
        V3_FEE,
    )

    onchain_pool = UniswapV3Pool(
        client.w3,
        pool_address,
    )

    pool = build_v3_pool(
        onchain_pool
    )

    print(
        f"\nPool: {pool_address}"
    )

    print("\nSTATE")
    print("-" * 60)

    print(
        f"sqrtPriceX96: "
        f"{pool.sqrt_price_x96}"
    )

    print(
        f"tick:         "
        f"{pool.tick}"
    )

    print(
        f"liquidity:    "
        f"{pool.liquidity}"
    )

    print(
        f"fee:          "
        f"{pool.fee}"
    )

    print(
        f"tick spacing: "
        f"{pool.tick_spacing}"
    )

    # --------------------------------------------------------
    # Example:
    #
    # 1 WETH
    #
    # WETH is token0 in this pool.
    # --------------------------------------------------------

    amount_in = 1 * 10**WETH_DECIMALS

    zero_for_one = (
        WETH_ADDRESS.lower()
        == pool.token0.lower()
    )

    result = pool.swap_exact_input(
        amount_in=amount_in,
        zero_for_one=zero_for_one,
    )

    print("\nSWAP")
    print("-" * 60)

    print(
        f"Input:        "
        f"{amount_in / 10**WETH_DECIMALS:.6f} WETH"
    )

    print(
        f"Output:       "
        f"{result.amount_out / 10**USDC_DECIMALS:.6f} USDC"
    )

    print(
        f"Fee:          "
        f"{result.fee_amount / 10**WETH_DECIMALS:.8f} WETH"
    )

    print(
        f"Ticks crossed:"
        f" {result.ticks_crossed}"
    )

    print("\nPRICE STATE")
    print("-" * 60)

    print(
        f"Tick before:  "
        f"{result.tick_before}"
    )

    print(
        f"Tick after:   "
        f"{result.tick_after}"
    )

    print(
        f"Sqrt before:  "
        f"{result.sqrt_price_before}"
    )

    print(
        f"Sqrt after:   "
        f"{result.sqrt_price_after}"
    )


if __name__ == "__main__":
    main()