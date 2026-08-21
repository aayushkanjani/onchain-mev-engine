from __future__ import annotations

from dataclasses import dataclass

from src.amm.pool import AMMPool
from src.amm.v3.pool import V3Pool


# ============================================================
# V2 ↔ V2 ARBITRAGE
# ============================================================

@dataclass
class ArbitrageResult:
    """
    Result of a two-pool constant-product arbitrage simulation.

    The simulation does NOT mutate either pool.
    """

    amount_in: float
    intermediate_amount: float
    final_amount: float
    profit: float
    profitable: bool


def simulate_arbitrage(
    buy_pool: AMMPool,
    sell_pool: AMMPool,
    amount_in: float,
) -> ArbitrageResult:
    """
    Simulate a two-pool arbitrage.

    We assume:

        token_x -> token_y on buy_pool
        token_y -> token_x on sell_pool

    Example:

        ETH -> USDC on pool A
        USDC -> ETH on pool B

    The pools are NOT modified.
    """

    if amount_in <= 0:
        raise ValueError(
            "amount_in must be positive"
        )

    # --------------------------------------------------------
    # Leg 1
    # --------------------------------------------------------

    intermediate_amount = buy_pool.get_amount_out(
        amount_in=amount_in,
        token_in=buy_pool.token_x,
    )

    # --------------------------------------------------------
    # Leg 2
    # --------------------------------------------------------

    final_amount = sell_pool.get_amount_out(
        amount_in=intermediate_amount,
        token_in=sell_pool.token_y,
    )

    # --------------------------------------------------------
    # Profit
    # --------------------------------------------------------

    profit = final_amount - amount_in

    return ArbitrageResult(
        amount_in=amount_in,
        intermediate_amount=intermediate_amount,
        final_amount=final_amount,
        profit=profit,
        profitable=profit > 0,
    )


# ============================================================
# V2 → V3 ARBITRAGE
# ============================================================

@dataclass
class V2V3ArbitrageResult:
    amount_in: int

    weth_bought: int
    usdc_received: int

    v2_fee: int
    v3_fee: int

    gross_profit: int
    net_profit: int

    v3_ticks_crossed: list[int]


def simulate_v2_to_v3(
    amount_in: int,
    v2_pool: AMMPool,
    v3_pool: V3Pool,
    usdc_token: str,
    weth_token: str,
) -> V2V3ArbitrageResult:
    """
    Simulate:

        USDC -> WETH on V2
        WETH -> USDC on V3

    V2:
        Constant-product AMM.

    V3:
        Concentrated-liquidity swap engine using:

        - sqrtPriceX96
        - liquidity
        - fee
        - initialized ticks
        - tick crossing
        - liquidityNet
        - price movement
    """

    if amount_in <= 0:
        raise ValueError(
            "amount_in must be positive"
        )

    # ========================================================
    # LEG 1
    #
    # USDC -> WETH on V2
    # ========================================================

    weth_bought_float = v2_pool.get_amount_out(
        amount_in=amount_in,
        token_in=usdc_token,
    )

    weth_bought = int(weth_bought_float)

    v2_fee = int(
        v2_pool.calculate_fee(amount_in)
    )

    if weth_bought <= 0:

        return V2V3ArbitrageResult(
            amount_in=amount_in,
            weth_bought=0,
            usdc_received=0,
            v2_fee=v2_fee,
            v3_fee=0,
            gross_profit=-amount_in,
            net_profit=-amount_in,
            v3_ticks_crossed=[],
        )

    # ========================================================
    # LEG 2
    #
    # WETH -> USDC on V3
    # ========================================================

    if weth_token.lower() == v3_pool.token0.lower():

        # token0 -> token1
        zero_for_one = True

    elif weth_token.lower() == v3_pool.token1.lower():

        # token1 -> token0
        zero_for_one = False

    else:

        raise ValueError(
            "WETH is not token0 or token1 of V3 pool"
        )

    v3_result = v3_pool.swap_exact_input(
        amount_in=weth_bought,
        zero_for_one=zero_for_one,
    )

    usdc_received = v3_result.amount_out

    # ========================================================
    # PROFIT
    # ========================================================

    gross_profit = (
        usdc_received - amount_in
    )

    net_profit = gross_profit

    return V2V3ArbitrageResult(
        amount_in=amount_in,
        weth_bought=weth_bought,
        usdc_received=usdc_received,
        v2_fee=v2_fee,
        v3_fee=v3_result.fee_amount,
        gross_profit=gross_profit,
        net_profit=net_profit,
        v3_ticks_crossed=v3_result.ticks_crossed,
    )