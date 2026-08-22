from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

from src.blockchain.swap_detection import PoolMetadata


@dataclass(frozen=True)
class MarketObservation:
    """
    Normalized market observation for one liquidity pool.

    price_token1_per_token0:
        Price of token0 denominated in token1.

    price_token0_per_token1:
        Inverse price.
    """

    pool_address: str
    dex: str
    version: str
    token0: str
    token1: str

    price_token1_per_token0: float
    price_token0_per_token1: float

    block_number: int | None = None
    transaction_index: int | None = None
    log_index: int | None = None


@dataclass(frozen=True)
class ArbitrageOpportunity:
    """
    Candidate cross-pool arbitrage opportunity.

    This object represents a detection result only.

    It does NOT execute a transaction.
    """

    token0: str
    token1: str

    buy_pool: str
    sell_pool: str

    buy_price: float
    sell_price: float

    gross_spread: float
    gross_spread_percent: float

    estimated_profit_per_token0: float

    block_number: int | None = None


class OpportunityDetector:
    """
    Detect cross-pool price discrepancies.

    Architecture:

        SwapEvent
            ↓
        MarketObservation
            ↓
        pair pools by token pair
            ↓
        compare prices
            ↓
        ArbitrageOpportunity
    """

    def __init__(
        self,
        min_spread_percent: float = 0.10,
    ):
        if min_spread_percent < 0:
            raise ValueError(
                "min_spread_percent must be non-negative"
            )

        self.min_spread_percent = min_spread_percent

    # ========================================================
    # OBSERVATION
    # ========================================================

    @staticmethod
    def observation_from_price(
        pool: PoolMetadata,
        price_token1_per_token0: float,
        block_number: int | None = None,
        transaction_index: int | None = None,
        log_index: int | None = None,
    ) -> MarketObservation:
        """
        Create a normalized market observation.
        """

        if price_token1_per_token0 <= 0:
            raise ValueError(
                "price must be positive"
            )

        return MarketObservation(
            pool_address=pool.address,
            dex=pool.dex,
            version=pool.version,
            token0=pool.token0,
            token1=pool.token1,
            price_token1_per_token0=(
                price_token1_per_token0
            ),
            price_token0_per_token1=(
                1.0 / price_token1_per_token0
            ),
            block_number=block_number,
            transaction_index=transaction_index,
            log_index=log_index,
        )

    # ========================================================
    # GROUPING
    # ========================================================

    @staticmethod
    def _pair_key(
        observation: MarketObservation,
    ) -> tuple[str, str]:
        """
        Return a canonical token pair key.
        """

        return tuple(
            sorted(
                [
                    observation.token0.lower(),
                    observation.token1.lower(),
                ]
            )
        )

    def group_by_pair(
        self,
        observations: Iterable[MarketObservation],
    ) -> dict[
        tuple[str, str],
        list[MarketObservation],
    ]:
        """
        Group observations by token pair.
        """

        grouped: dict[
            tuple[str, str],
            list[MarketObservation],
        ] = {}

        for observation in observations:

            key = self._pair_key(
                observation
            )

            grouped.setdefault(
                key,
                [],
            ).append(
                observation
            )

        return grouped

    # ========================================================
    # PAIR ANALYSIS
    # ========================================================

    def detect_pair(
        self,
        observations: list[MarketObservation],
    ) -> list[ArbitrageOpportunity]:
        """
        Compare all pools for one token pair.
        """

        opportunities: list[
            ArbitrageOpportunity
        ] = []

        if len(observations) < 2:
            return opportunities

        for first, second in combinations(
            observations,
            2,
        ):
            opportunity = (
                self._compare(
                    first,
                    second,
                )
            )

            if opportunity is not None:
                opportunities.append(
                    opportunity
                )

        return sorted(
            opportunities,
            key=lambda item: (
                -item.gross_spread_percent
            ),
        )

    # ========================================================
    # ALL OBSERVATIONS
    # ========================================================

    def detect(
        self,
        observations: Iterable[MarketObservation],
    ) -> list[ArbitrageOpportunity]:
        """
        Detect opportunities across all observations.
        """

        grouped = self.group_by_pair(
            observations
        )

        opportunities: list[
            ArbitrageOpportunity
        ] = []

        for pair_observations in grouped.values():

            opportunities.extend(
                self.detect_pair(
                    pair_observations
                )
            )

        return sorted(
            opportunities,
            key=lambda item: (
                -item.gross_spread_percent
            ),
        )

    # ========================================================
    # COMPARISON
    # ========================================================

    def _compare(
        self,
        first: MarketObservation,
        second: MarketObservation,
    ) -> ArbitrageOpportunity | None:
        """
        Compare two pools.

        We normalize both pools to token1/token0.

        The cheaper pool is the buy side.
        The more expensive pool is the sell side.
        """

        if self._pair_key(first) != self._pair_key(
            second
        ):
            return None

        if (
            first.price_token1_per_token0
            <= second.price_token1_per_token0
        ):
            buy = first
            sell = second
        else:
            buy = second
            sell = first

        buy_price = (
            buy.price_token1_per_token0
        )

        sell_price = (
            sell.price_token1_per_token0
        )

        if buy_price <= 0:
            return None

        gross_spread = (
            sell_price
            - buy_price
        )

        gross_spread_percent = (
            gross_spread
            / buy_price
            * 100.0
        )

        if (
            gross_spread_percent
            < self.min_spread_percent
        ):
            return None

        return ArbitrageOpportunity(
            token0=buy.token0,
            token1=buy.token1,
            buy_pool=buy.pool_address,
            sell_pool=sell.pool_address,
            buy_price=buy_price,
            sell_price=sell_price,
            gross_spread=gross_spread,
            gross_spread_percent=(
                gross_spread_percent
            ),
            estimated_profit_per_token0=(
                gross_spread
            ),
            block_number=(
                sell.block_number
                if sell.block_number is not None
                else buy.block_number
            ),
        )