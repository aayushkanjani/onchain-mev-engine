from src.amm.v3.pool import V3Pool
from src.amm.v3.onchain import OnChainV3TickProvider

from src.blockchain.client import EthereumClient
from src.blockchain.uniswap_v2 import (
    WETH_ADDRESS,
    USDC_ADDRESS,
)
from src.blockchain.uniswap_v3 import (
    UniswapV3Factory,
    UniswapV3Pool,
)


V3_FEE = 500


def build_pool(client):

    factory = UniswapV3Factory(
        client.w3
    )

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

    sqrt_price_x96 = int(slot0[0])
    tick = int(slot0[1])

    liquidity = int(
        chain_pool.liquidity()
    )

    fee = int(
        chain_pool.fee()
    )

    tick_spacing = int(
        chain_pool.tick_spacing()
    )

    provider = OnChainV3TickProvider(
        chain_pool
    )

    return V3Pool(
        token0=chain_pool.token0(),
        token1=chain_pool.token1(),
        sqrt_price_x96=sqrt_price_x96,
        tick=tick,
        liquidity=liquidity,
        fee=fee,
        tick_spacing=tick_spacing,
        bitmap_provider=provider.bitmap,
        tick_provider=provider.tick,
    ), address


def main():

    client = EthereumClient()

    pool, address = build_pool(client)

    print("=" * 60)
    print("REAL V3 POOL")
    print("=" * 60)

    print("Pool:", address)
    print("Tick:", pool.tick)
    print("Liquidity:", pool.liquidity)
    print("Fee:", pool.fee)
    print("Tick spacing:", pool.tick_spacing)

    print("\nSIMULATING SWAP")

    amount_in = 1_000_000  # 1 USDC

    result = pool.swap_exact_input(
        amount_in=amount_in,
        zero_for_one=True,
    )

    print("Amount in:", result.amount_in)
    print("Amount out:", result.amount_out)
    print("Fee:", result.fee_amount)

    print(
        "Ticks crossed:",
        result.ticks_crossed,
    )

    print(
        "Tick:",
        result.tick_before,
        "→",
        result.tick_after,
    )


if __name__ == "__main__":
    main()