from src.blockchain.client import EthereumClient
from src.blockchain.uniswap_v2 import (
    UniswapV2Factory,
    UniswapV2Pool,
    WETH_ADDRESS,
    USDC_ADDRESS,
)

from src.amm.pool import AMMPool


WETH_DECIMALS = 18
USDC_DECIMALS = 6


def main():

    client = EthereumClient()

    # --------------------------------------------------
    # 1. Find the real Uniswap V2 pair
    # --------------------------------------------------

    factory = UniswapV2Factory(client.w3)

    pair_address = factory.get_pair(
        WETH_ADDRESS,
        USDC_ADDRESS,
    )

    pool = UniswapV2Pool(
        client.w3,
        pair_address,
    )

    # --------------------------------------------------
    # 2. Read real reserves
    # --------------------------------------------------

    token0 = pool.token0()
    reserves = pool.reserves()

    if token0.lower() == USDC_ADDRESS.lower():

        usdc_raw = reserves["reserve0"]
        weth_raw = reserves["reserve1"]

    else:

        weth_raw = reserves["reserve0"]
        usdc_raw = reserves["reserve1"]

    # --------------------------------------------------
    # 3. Convert raw blockchain units
    # --------------------------------------------------

    usdc = usdc_raw / 10**USDC_DECIMALS
    weth = weth_raw / 10**WETH_DECIMALS

    # --------------------------------------------------
    # 4. Create AMM using REAL blockchain state
    # --------------------------------------------------

    amm = AMMPool(
        token_x=USDC_ADDRESS,
        token_y=WETH_ADDRESS,
        reserve_x=usdc,
        reserve_y=weth,
        fee_rate=0.003,
    )

    # --------------------------------------------------
    # 5. Display pool state
    # --------------------------------------------------

    print("=" * 60)
    print("REAL UNISWAP → AMM ENGINE")
    print("=" * 60)

    print(f"Pool: {pair_address}")

    print(f"\nUSDC reserve: {usdc:,.2f}")
    print(f"WETH reserve: {weth:,.6f}")

    print(
        f"\nSpot price: "
        f"${amm.spot_price_y_in_x:,.2f} USDC/WETH"
    )

    print(f"k: {amm.k:,.2f}")

    # --------------------------------------------------
    # 6. Simulate a real trade
    # --------------------------------------------------

    amount_in = 1_000

    amount_out = amm.get_amount_out(
        amount_in=amount_in,
        token_in=USDC_ADDRESS,
    )

    effective_price = amount_in / amount_out

    print("\n" + "=" * 60)
    print("SIMULATED SWAP")
    print("=" * 60)

    print(f"USDC in:          ${amount_in:,.2f}")
    print(f"WETH out:         {amount_out:.8f}")
    print(f"Effective price:  ${effective_price:,.2f}")

    fee = amm.calculate_fee(amount_in)

    print(f"Trading fee:      ${fee:.2f}")

    # --------------------------------------------------
    # 7. Execute the simulated swap
    # --------------------------------------------------

    amm.swap(
        amount_in=amount_in,
        token_in=USDC_ADDRESS,
    )

    print("\n" + "=" * 60)
    print("POOL AFTER SWAP")
    print("=" * 60)

    print(f"USDC reserve: {amm.reserve_x:,.2f}")
    print(f"WETH reserve: {amm.reserve_y:,.6f}")

    print(
        f"New spot price: "
        f"${amm.spot_price_y_in_x:,.2f}"
    )


if __name__ == "__main__":
    main()