from __future__ import annotations

from dataclasses import dataclass

from src.amm.pool import AMMPool
from src.amm.v3.pool import V3Pool


# ============================================================
# TOKEN DECIMALS
# ============================================================

USDC_DECIMALS = 6
WETH_DECIMALS = 18


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

    # Human-readable USDC amount
    amount_in: float

    # Human-readable WETH amount
    weth_bought: float

    # Human-readable USDC amount
    usdc_received: float

    # Fees
    v2_fee: float
    v3_fee: float

    # Profit
    gross_profit: float

    # Gas in USD
    gas_cost: float

    # Profit after gas
    net_profit: float

    profitable: bool

    # Useful execution information
    v3_ticks_crossed: list[int]


def simulate_v2_to_v3(
    amount_in: float,
    v2_pool: AMMPool,
    v3_pool: V3Pool,
    usdc_token: str,
    weth_token: str,
    gas_used: int = 250_000,
    gas_price_gwei: float = 20.0,
    eth_price: float = 2_500.0,
) -> V2V3ArbitrageResult:
    """
    Simulate:

        USDC -> WETH on V2
        WETH -> USDC on V3

    Important:

    V2 AMMPool uses human-readable token amounts.

    V3Pool uses raw integer token amounts.

    Therefore the boundary between V2 and V3 explicitly
    performs decimal conversion.

    This keeps the two engines internally consistent.
    """

    if amount_in <= 0:
        raise ValueError(
            "amount_in must be positive"
        )

    # ========================================================
    # LEG 1
    #
    # USDC -> WETH on V2
    #
    # V2 uses human-readable units.
    # ========================================================

    weth_bought = v2_pool.get_amount_out(
        amount_in=amount_in,
        token_in=usdc_token,
    )

    v2_fee = v2_pool.calculate_fee(
        amount_in
    )

    if weth_bought <= 0:

        gas_cost_native = (
            gas_used
            * gas_price_gwei
            / 1_000_000_000
        )

        gas_cost = (
            gas_cost_native
            * eth_price
        )

        gross_profit = -amount_in

        net_profit = (
            gross_profit
            - gas_cost
        )

        return V2V3ArbitrageResult(
            amount_in=amount_in,
            weth_bought=0.0,
            usdc_received=0.0,
            v2_fee=v2_fee,
            v3_fee=0.0,
            gross_profit=gross_profit,
            gas_cost=gas_cost,
            net_profit=net_profit,
            profitable=False,
            v3_ticks_crossed=[],
        )

    # ========================================================
    # DECIMAL BOUNDARY
    #
    # Human WETH → raw WETH
    #
    # Example:
    #
    # 0.04 WETH
    #
    # becomes:
    #
    # 40,000,000,000,000,000
    # ========================================================

    weth_raw = int(
        weth_bought * 10**WETH_DECIMALS
    )

    if weth_raw <= 0:

        gas_cost_native = (
            gas_used
            * gas_price_gwei
            / 1_000_000_000
        )

        gas_cost = (
            gas_cost_native
            * eth_price
        )

        gross_profit = -amount_in

        net_profit = (
            gross_profit
            - gas_cost
        )

        return V2V3ArbitrageResult(
            amount_in=amount_in,
            weth_bought=weth_bought,
            usdc_received=0.0,
            v2_fee=v2_fee,
            v3_fee=0.0,
            gross_profit=gross_profit,
            gas_cost=gas_cost,
            net_profit=net_profit,
            profitable=False,
            v3_ticks_crossed=[],
        )

    # ========================================================
    # LEG 2
    #
    # WETH -> USDC on V3
    #
    # Determine swap direction from token ordering.
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

    # ========================================================
    # REAL V3 SWAP
    # ========================================================

    v3_result = v3_pool.swap_exact_input(
        amount_in=weth_raw,
        zero_for_one=zero_for_one,
    )

    # V3 returns raw USDC.
    usdc_received_raw = v3_result.amount_out

    # Convert raw USDC → human-readable USDC.
    usdc_received = (
        usdc_received_raw
        / 10**USDC_DECIMALS
    )

    # V3 fee is denominated in input token = WETH.
    v3_fee_weth = (
        v3_result.fee_amount
        / 10**WETH_DECIMALS
    )

    # ========================================================
    # PROFIT
    # ========================================================

    gross_profit = (
        usdc_received
        - amount_in
    )

    # ========================================================
    # GAS
    # ========================================================

    gas_cost_native = (
        gas_used
        * gas_price_gwei
        / 1_000_000_000
    )

    gas_cost = (
        gas_cost_native
        * eth_price
    )

    # ========================================================
    # NET PROFIT
    # ========================================================

    net_profit = (
        gross_profit
        - gas_cost
    )

    profitable = (
        net_profit > 0
    )

    return V2V3ArbitrageResult(
        amount_in=amount_in,
        weth_bought=weth_bought,
        usdc_received=usdc_received,
        v2_fee=v2_fee,
        v3_fee=v3_fee_weth,
        gross_profit=gross_profit,
        gas_cost=gas_cost,
        net_profit=net_profit,
        profitable=profitable,
        v3_ticks_crossed=v3_result.ticks_crossed,
    )