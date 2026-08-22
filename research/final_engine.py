from __future__ import annotations

from src.amm.pool import AMMPool
from src.mev.execution_gate import ExecutionGate
from src.mev.execution_simulator import ExecutionSimulator
from src.mev.risk import RiskLimits, RiskManager
from src.mev.strategies import StrategyEngine


def print_decision(
    title: str,
    decision,
) -> None:

    print()
    print("-" * 70)
    print(title)
    print("-" * 70)

    print(
        f"Strategy:       {decision.strategy}"
    )

    print(
        f"Amount in:      "
        f"{decision.amount_in:.6f}"
    )

    print(
        f"Net profit:     "
        f"${decision.net_profit:.6f}"
    )

    print(
        f"Decision:       "
        f"{decision.action}"
    )

    print(
        f"Risk approved:  "
        f"{decision.risk.approved}"
    )

    if decision.risk.warnings:

        print()
        print("Warnings:")

        for warning in decision.risk.warnings:

            print(
                f"  - {warning}"
            )

    if decision.risk.reasons:

        print()
        print("Rejection reasons:")

        for reason in decision.risk.reasons:

            print(
                f"  - {reason}"
            )


def build_arbitrage_candidate(
    engine: StrategyEngine,
):
    """
    Create a deterministic synthetic arbitrage candidate.
    """

    from src.blockchain.swap_detection import (
        PoolMetadata,
    )

    from src.mev.opportunity import (
        OpportunityDetector,
    )

    buy_pool = AMMPool(
        token_x="USDC",
        token_y="WETH",
        reserve_x=1_000_000.0,
        reserve_y=500.0,
        fee_rate=0.003,
    )

    sell_pool = AMMPool(
        token_x="USDC",
        token_y="WETH",
        reserve_x=1_000_000.0,
        reserve_y=480.0,
        fee_rate=0.003,
    )

    pool_a = PoolMetadata(
        address=(
            "0x0000000000000000000000000000000000000011"
        ),
        dex="DemoDEX",
        version="V2",
        token0="USDC",
        token1="WETH",
    )

    pool_b = PoolMetadata(
        address=(
            "0x0000000000000000000000000000000000000022"
        ),
        dex="DemoDEX",
        version="V2",
        token0="USDC",
        token1="WETH",
    )

    detector = OpportunityDetector(
        min_spread_percent=0.1
    )

    observations = [
        detector.observation_from_price(
            pool=pool_a,
            price_token1_per_token0=0.000500,
            block_number=1,
        ),
        detector.observation_from_price(
            pool=pool_b,
            price_token1_per_token0=0.000520,
            block_number=1,
        ),
    ]

    opportunities = detector.detect(
        observations
    )

    if not opportunities:
        return None

    return engine.evaluate_arbitrage(
        opportunity=opportunities[0],
        buy_pool=buy_pool,
        sell_pool=sell_pool,
        amount_in=10_000.0,
    )


def build_sandwich_candidate(
    engine: StrategyEngine,
):
    """
    Create a deterministic synthetic sandwich candidate.
    """

    pool = AMMPool(
        token_x="USDC",
        token_y="WETH",
        reserve_x=1_000_000.0,
        reserve_y=500.0,
        fee_rate=0.003,
    )

    return engine.evaluate_sandwich(
        pool=pool,
        victim_amount_in=25_000.0,
        victim_token_in="USDC",
        attacker_amount_in=5_000.0,
    )


def main() -> None:

    print("=" * 70)
    print(
        "ON-CHAIN MEV ENGINE — FINAL EXECUTION PIPELINE"
    )
    print("=" * 70)

    # ========================================================
    # EXECUTION SIMULATOR
    # ========================================================

    simulator = ExecutionSimulator(
        gas_used=250_000,
        gas_price_gwei=20.0,
        native_token_price=2_500.0,
    )

    strategy_engine = StrategyEngine(
        simulator
    )

    # ========================================================
    # RISK CONFIGURATION
    # ========================================================

    limits = RiskLimits(
        min_net_profit_usd=25.0,
        max_gas_cost_usd=100.0,
        max_trade_size=100_000.0,
        max_slippage_percent=1.0,
        max_position_size=100_000.0,
    )

    risk_manager = RiskManager(
        limits
    )

    execution_gate = ExecutionGate(
        risk_manager
    )

    print()
    print("Risk controls configured.")

    print(
        f"Minimum profit: "
        f"${limits.min_net_profit_usd:.2f}"
    )

    print(
        f"Maximum gas:    "
        f"${limits.max_gas_cost_usd:.2f}"
    )

    print(
        f"Maximum trade:  "
        f"{limits.max_trade_size:.2f}"
    )

    print(
        f"Maximum slippage:"
        f" {limits.max_slippage_percent:.2f}%"
    )

    # ========================================================
    # ARBITRAGE
    # ========================================================

    print()
    print("-" * 70)
    print("ARBITRAGE")
    print("-" * 70)

    arbitrage_candidate = (
        build_arbitrage_candidate(
            strategy_engine
        )
    )

    if arbitrage_candidate is not None:

        arbitrage_decision = (
            execution_gate.evaluate(
                candidate=arbitrage_candidate,
                slippage_percent=0.25,
            )
        )

        print_decision(
            "Cross-Pool Arbitrage",
            arbitrage_decision,
        )

    else:

        print(
            "No arbitrage candidate detected."
        )

    # ========================================================
    # SANDWICH
    # ========================================================

    print()
    print("-" * 70)
    print("SANDWICH")
    print("-" * 70)

    sandwich_candidate = (
        build_sandwich_candidate(
            strategy_engine
        )
    )

    sandwich_decision = (
        execution_gate.evaluate(
            candidate=sandwich_candidate,
            slippage_percent=0.50,
        )
    )

    print_decision(
        "Victim Transaction Sandwich",
        sandwich_decision,
    )

    # ========================================================
    # FINAL STATUS
    # ========================================================

    print()
    print("=" * 70)
    print("FINAL PIPELINE COMPLETE")
    print("=" * 70)

    print()
    print(
        "Pipeline:"
    )

    print(
        "Ethereum data"
    )

    print(
        "    ↓"
    )

    print(
        "Swap detection"
    )

    print(
        "    ↓"
    )

    print(
        "Market observations"
    )

    print(
        "    ↓"
    )

    print(
        "Opportunity detection"
    )

    print(
        "    ↓"
    )

    print(
        "Execution simulation"
    )

    print(
        "    ↓"
    )

    print(
        "Strategy selection"
    )

    print(
        "    ↓"
    )

    print(
        "Risk management"
    )

    print(
        "    ↓"
    )

    print(
        "Execution gate"
    )

    print(
        "    ↓"
    )

    print(
        "Paper execution decision"
    )

    print()
    print(
        "No private keys were loaded."
    )

    print(
        "No transactions were signed."
    )

    print(
        "No transactions were broadcast."
    )


if __name__ == "__main__":
    main()