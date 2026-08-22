from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.mev.execution_simulator import (
    ExecutionSimulator,
    SimulationResult,
)
from src.mev.opportunity import (
    ArbitrageOpportunity,
)


class StrategyType(str, Enum):
    """
    Supported MEV strategy types.
    """

    ARBITRAGE = "arbitrage"
    SANDWICH = "sandwich"


@dataclass(frozen=True)
class StrategyCandidate:
    """
    Normalized strategy candidate.

    This represents a simulated execution opportunity.

    No transaction is signed or broadcast.
    """

    strategy: StrategyType

    profitable: bool

    gross_profit: float
    gas_cost: float
    net_profit: float

    amount_in: float

    details: dict[str, Any]


class ArbitrageStrategy:
    """
    Cross-pool arbitrage strategy.

    The strategy converts a detected
    ArbitrageOpportunity into an execution simulation.
    """

    strategy_type = StrategyType.ARBITRAGE

    def __init__(
        self,
        simulator: ExecutionSimulator,
    ):
        self.simulator = simulator

    def evaluate(
        self,
        opportunity: ArbitrageOpportunity,
        buy_pool: Any,
        sell_pool: Any,
        amount_in: float,
    ) -> StrategyCandidate:
        """
        Evaluate one arbitrage opportunity.
        """

        if amount_in <= 0:
            raise ValueError(
                "amount_in must be positive"
            )

        result = self.simulator.simulate_arbitrage(
            buy_pool=buy_pool,
            sell_pool=sell_pool,
            amount_in=amount_in,
            token_in=opportunity.token0,
        )

        return self._candidate(
            result=result,
            amount_in=amount_in,
            opportunity=opportunity,
        )

    def _candidate(
        self,
        result: SimulationResult,
        amount_in: float,
        opportunity: ArbitrageOpportunity,
    ) -> StrategyCandidate:
        return StrategyCandidate(
            strategy=self.strategy_type,
            profitable=result.profitable,
            gross_profit=result.gross_profit,
            gas_cost=result.gas_cost,
            net_profit=result.net_profit,
            amount_in=amount_in,
            details={
                "buy_pool": opportunity.buy_pool,
                "sell_pool": opportunity.sell_pool,
                "token0": opportunity.token0,
                "token1": opportunity.token1,
                "spread_percent": (
                    opportunity.gross_spread_percent
                ),
            },
        )


class SandwichStrategy:
    """
    Sandwich strategy simulator.

    This models:

        attacker front-run
        victim swap
        attacker back-run

    It is intentionally simulation-only.
    """

    strategy_type = StrategyType.SANDWICH

    def __init__(
        self,
        simulator: ExecutionSimulator,
    ):
        self.simulator = simulator

    def evaluate(
        self,
        pool: Any,
        victim_amount_in: float,
        victim_token_in: str,
        attacker_amount_in: float,
    ) -> StrategyCandidate:
        """
        Evaluate a sandwich scenario.
        """

        if victim_amount_in <= 0:
            raise ValueError(
                "victim_amount_in must be positive"
            )

        if attacker_amount_in <= 0:
            raise ValueError(
                "attacker_amount_in must be positive"
            )

        result = self.simulator.simulate_sandwich(
            pool=pool,
            victim_amount_in=victim_amount_in,
            victim_token_in=victim_token_in,
            attacker_amount_in=attacker_amount_in,
        )

        return StrategyCandidate(
            strategy=self.strategy_type,
            profitable=result.profitable,
            gross_profit=result.gross_profit,
            gas_cost=result.gas_cost,
            net_profit=result.net_profit,
            amount_in=attacker_amount_in,
            details={
                "victim_amount_in": victim_amount_in,
                "victim_token_in": victim_token_in,
                "attacker_amount_in": attacker_amount_in,
                "trades": len(result.trades),
            },
        )


class StrategyEngine:
    """
    Select and evaluate MEV strategies.

    The engine does not execute transactions.

    It only ranks simulated candidates.
    """

    def __init__(
        self,
        simulator: ExecutionSimulator,
    ):
        self.simulator = simulator

        self.arbitrage = ArbitrageStrategy(
            simulator
        )

        self.sandwich = SandwichStrategy(
            simulator
        )

    # ========================================================
    # ARBITRAGE
    # ========================================================

    def evaluate_arbitrage(
        self,
        opportunity: ArbitrageOpportunity,
        buy_pool: Any,
        sell_pool: Any,
        amount_in: float,
    ) -> StrategyCandidate:
        return self.arbitrage.evaluate(
            opportunity=opportunity,
            buy_pool=buy_pool,
            sell_pool=sell_pool,
            amount_in=amount_in,
        )

    # ========================================================
    # SANDWICH
    # ========================================================

    def evaluate_sandwich(
        self,
        pool: Any,
        victim_amount_in: float,
        victim_token_in: str,
        attacker_amount_in: float,
    ) -> StrategyCandidate:
        return self.sandwich.evaluate(
            pool=pool,
            victim_amount_in=victim_amount_in,
            victim_token_in=victim_token_in,
            attacker_amount_in=attacker_amount_in,
        )

    # ========================================================
    # RANKING
    # ========================================================

    @staticmethod
    def rank(
        candidates: list[StrategyCandidate],
    ) -> list[StrategyCandidate]:
        """
        Rank candidates by net profit.
        """

        return sorted(
            candidates,
            key=lambda candidate: (
                candidate.net_profit
            ),
            reverse=True,
        )

    # ========================================================
    # PROFITABLE ONLY
    # ========================================================

    @staticmethod
    def profitable_only(
        candidates: list[StrategyCandidate],
    ) -> list[StrategyCandidate]:
        """
        Remove candidates that are not profitable.
        """

        return [
            candidate
            for candidate in candidates
            if candidate.profitable
        ]