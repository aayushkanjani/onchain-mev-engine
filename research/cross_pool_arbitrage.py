from dataclasses import dataclass

from src.amm.pool import AMMPool
from src.amm.optimizer import grid_search

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

# Uniswap V3 fee tier:
# 500 = 0.05%
V3_FEE = 500


@dataclass
class ArbitrageResult:
    amount_in: float
    weth_bought: float
    usdc_received: float

    gross_profit: float
    net_profit: float

    v2_fee: float
    v3_fee: float


def get_v2_pool(client) -> AMMPool:
    """
    Read the real Uniswap V2 WETH/USDC pool
    and convert its reserves into human units.
    """

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


def get_v3_price(client) -> float:
    """
    Read the current Uniswap V3 spot price.

    This is still a simplified V3 model:
    we use the current spot price rather than
    simulating movement across V3 ticks.
    """

    factory = UniswapV3Factory(client.w3)

    address = factory.get_pool(
        WETH_ADDRESS,
        USDC_ADDRESS,
        V3_FEE,
    )

    pool = UniswapV3Pool(
        client.w3,
        address,
    )

    token0 = pool.token0()

    sqrt_price_x96 = pool.slot0()[0]

    # sqrtPriceX96 represents:
    #
    # sqrt(token1_raw / token0_raw) * 2^96
    #
    # Therefore:
    #
    # raw_price =
    # token1_raw / token0_raw

    raw_price = (
        sqrt_price_x96 / 2**96
    ) ** 2

    if token0.lower() == USDC_ADDRESS.lower():

        # token0 = USDC
        # token1 = WETH
        #
        # raw_price = WETH_raw / USDC_raw
        #
        # Convert to human WETH / USDC
        # and then invert to get USDC / WETH.

        weth_per_usdc = (
            raw_price
            * 10 ** (
                USDC_DECIMALS
                - WETH_DECIMALS
            )
        )

        return 1 / weth_per_usdc

    else:

        # token0 = WETH
        # token1 = USDC
        #
        # raw_price = USDC_raw / WETH_raw
        #
        # Convert directly to human USDC / WETH.

        return (
            raw_price
            * 10 ** (
                WETH_DECIMALS
                - USDC_DECIMALS
            )
        )


def simulate(
    amount_in: float,
    v2: AMMPool,
    v3_price: float,
) -> ArbitrageResult:
    """
    Simulate:

        USDC → WETH on V2
        WETH → USDC on V3

    V2 uses its real constant-product curve.

    V3 currently uses only its spot price.

    Therefore this is an approximation until
    we implement the V3 tick/liquidity simulator.
    """

    if amount_in <= 0:
        raise ValueError(
            "amount_in must be positive"
        )

    # =================================================
    # LEG 1
    #
    # USDC → WETH on V2
    # =================================================

    weth_bought = v2.get_amount_out(
        amount_in=amount_in,
        token_in=USDC_ADDRESS,
    )

    v2_fee = v2.calculate_fee(
        amount_in
    )

    # =================================================
    # LEG 2
    #
    # WETH → USDC on V3
    #
    # Current approximation:
    #
    # WETH × V3 spot price
    # =================================================

    gross_usdc = (
        weth_bought * v3_price
    )

    # V3 fee = 0.05%

    v3_fee = (
        gross_usdc
        * V3_FEE
        / 1_000_000
    )

    usdc_received = (
        gross_usdc - v3_fee
    )

    # =================================================
    # PNL
    # =================================================

    gross_profit = (
        gross_usdc
        - amount_in
    )

    net_profit = (
        usdc_received
        - amount_in
    )

    return ArbitrageResult(
        amount_in=amount_in,
        weth_bought=weth_bought,
        usdc_received=usdc_received,
        gross_profit=gross_profit,
        net_profit=net_profit,
        v2_fee=v2_fee,
        v3_fee=v3_fee,
    )


def main():

    client = EthereumClient()

    # =================================================
    # LOAD REAL MARKET DATA
    # =================================================

    v2 = get_v2_pool(client)

    v3_price = get_v3_price(client)

    # =================================================
    # MARKET
    # =================================================

    print("=" * 60)
    print("CROSS-POOL ARBITRAGE")
    print("=" * 60)

    print(
        f"\nV2 price: "
        f"${v2.spot_price_y_in_x:,.2f}"
    )

    print(
        f"V3 price: "
        f"${v3_price:,.2f}"
    )

    spread = (
        v3_price
        - v2.spot_price_y_in_x
    )

    spread_percentage = (
        spread
        / v2.spot_price_y_in_x
        * 100
    )

    print(
        f"Spread:   "
        f"${spread:,.2f} "
        f"({spread_percentage:.4f}%)"
    )

    # =================================================
    # SAMPLE TRADE SIZES
    # =================================================

    print("\nRESULTS")
    print("-" * 60)

    amounts = [
        100,
        1_000,
        5_000,
        10_000,
        25_000,
    ]

    for amount in amounts:

        result = simulate(
            amount,
            v2,
            v3_price,
        )

        print(
            f"${amount:>7,.0f}"
            f" → "
            f"${result.usdc_received:>10,.2f}"
            f" | PnL: "
            f"${result.net_profit:>8,.2f}"
        )

    # =================================================
    # OPTIMIZATION
    # =================================================

    def profit_function(
        amount: float,
    ) -> float:

        result = simulate(
            amount,
            v2,
            v3_price,
        )

        return result.net_profit

    best_amount, best_profit = grid_search(
        profit_function=profit_function,
        minimum=1,
        maximum=50_000,
        steps=5_000,
    )

    # =================================================
    # OPTIMAL TRADE
    # =================================================

    print("\nOPTIMAL TRADE")
    print("-" * 60)

    print(
        f"Trade size: "
        f"${best_amount:,.2f}"
    )

    print(
        f"Maximum PnL: "
        f"${best_profit:,.4f}"
    )

    if best_profit > 0:

        print(
            "Status: PROFITABLE"
        )

    else:

        print(
            "Status: NO ARBITRAGE"
        )

    # =================================================
    # IMPORTANT MODEL LIMITATION
    # =================================================

    print("\nMODEL")
    print("-" * 60)

    print(
        "V2: real constant-product swap"
    )

    print(
        "V3: spot-price approximation"
    )

    print(
        "Next: real V3 tick/liquidity simulation"
    )


if __name__ == "__main__":
    main()