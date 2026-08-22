from __future__ import annotations

from src.amm.pool import AMMPool
from src.mev.execution_simulator import (
    ExecutionSimulator,
)
from src.mev.strategies import (
    StrategyEngine,
)


def print_candidate(
    name: str,
    candidate,
) -> None:

    print()
    print("-" * 70)
    print(name)
    print("-" * 70)

    print(
        f"Strategy:       {candidate.strategy.value}"
    )

    print(
        f"Amount in:      {candidate.amount_in:.6f}"
    )

    print(
        f"Gross profit:   ${candidate.gross_profit:.6f}"
    )

    print(
        f"Gas cost:       ${candidate.gas_cost:.6f}"
    )

    print(
        f"Net profit:     ${candidate.net_profit:.6f}"
    )

    print(
        f"Profitable:     {candidate.profitable}"
    )


def main() -> None:

    print("=" * 70)
    print(
        "ON-CHAIN MEV ENGINE — EXECUTION SIMULATION"
    )
    print("=" * 70)

    # ========================================================
    # SIMULATOR
    # ========================================================

    simulator = ExecutionSimulator(
        gas_used=250_000,
        gas_price_gwei=20.0,
        native_token_price=2_500.0,
    )

    engine = StrategyEngine(
        simulator
    )

    print()
    print("Execution simulator configured.")

    print(
        f"Gas used:        {simulator.gas_used}"
    )

    print(
        f"Gas price:       "
        f"{simulator.gas_price_gwei} gwei"
    )

    print(
        f"Native price:    "
        f"${simulator.native_token_price:.2f}"
    )

    print(
        f"Gas cost:        "
        f"${simulator.gas_cost_usd:.2f}"
    )

    # ========================================================
    # ARBITRAGE DEMO
    # ========================================================

    print()
    print("-" * 70)
    print("ARBITRAGE SIMULATION")
    print("-" * 70)

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

    # --------------------------------------------------------
    # Synthetic opportunity.
    #
    # This is deliberately local simulation data.
    # No real transaction is executed.
    # --------------------------------------------------------

    from src.blockchain.swap_detection import (
        PoolMetadata,
    )

    from src.mev.opportunity import (
        OpportunityDetector,
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

    if opportunities:

        opportunity = opportunities[0]

        candidate = engine.evaluate_arbitrage(
            opportunity=opportunity,
            buy_pool=buy_pool,
            sell_pool=sell_pool,
            amount_in=10_000.0,
        )

        print_candidate(
            "Cross-Pool Arbitrage",
            candidate,
        )

    # ========================================================
    # SANDWICH DEMO
    # ========================================================

    print()
    print("-" * 70)
    print("SANDWICH SIMULATION")
    print("-" * 70)

    sandwich_pool = AMMPool(
        token_x="USDC",
        token_y="WETH",
        reserve_x=1_000_000.0,
        reserve_y=500.0,
        fee_rate=0.003,
    )

    sandwich_candidate = (
        engine.evaluate_sandwich(
            pool=sandwich_pool,
            victim_amount_in=25_000.0,
            victim_token_in="USDC",
            attacker_amount_in=5_000.0,
        )
    )

    print_candidate(
        "Victim Transaction Sandwich Model",
        sandwich_candidate,
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("EXECUTION SIMULATION COMPLETE")
    print("=" * 70)

    print()
    print(
        "No transactions were signed or broadcast."
    )

    print(
        "All MEV strategies were evaluated "
        "against copied local pool state."
    )


if __name__ == "__main__":
    main()