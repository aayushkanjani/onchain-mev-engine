from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskLimits:
    """
    Safety limits for paper execution.

    These limits are evaluated before an opportunity is allowed
    to proceed to the execution decision layer.
    """

    min_net_profit_usd: float = 25.0
    max_gas_cost_usd: float = 100.0
    max_trade_size: float = 100_000.0
    max_slippage_percent: float = 1.0
    max_position_size: float = 100_000.0
    require_profitable: bool = True


@dataclass(frozen=True)
class RiskAssessment:
    """
    Result of evaluating an opportunity against risk limits.
    """

    approved: bool
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def rejected(self) -> bool:
        return not self.approved


class RiskManager:
    """
    Evaluate simulated MEV opportunities against safety limits.

    This class does not execute transactions.

    Architecture:

        Strategy Candidate
              ↓
        RiskManager
              ↓
        RiskAssessment
              ↓
        Execution Gate
    """

    def __init__(
        self,
        limits: RiskLimits | None = None,
    ) -> None:

        self.limits = (
            limits
            if limits is not None
            else RiskLimits()
        )

        self._validate_limits()

    def _validate_limits(self) -> None:
        """
        Validate configured safety limits.
        """

        if self.limits.min_net_profit_usd < 0:
            raise ValueError(
                "min_net_profit_usd must be non-negative"
            )

        if self.limits.max_gas_cost_usd < 0:
            raise ValueError(
                "max_gas_cost_usd must be non-negative"
            )

        if self.limits.max_trade_size <= 0:
            raise ValueError(
                "max_trade_size must be positive"
            )

        if self.limits.max_slippage_percent < 0:
            raise ValueError(
                "max_slippage_percent must be non-negative"
            )

        if self.limits.max_position_size <= 0:
            raise ValueError(
                "max_position_size must be positive"
            )

    def evaluate(
        self,
        candidate,
        slippage_percent: float = 0.0,
    ) -> RiskAssessment:
        """
        Evaluate a strategy candidate.

        The candidate is intentionally duck-typed so this layer
        can work with arbitrage and sandwich candidates without
        coupling the risk system to a particular strategy class.
        """

        reasons: list[str] = []
        warnings: list[str] = []

        amount_in = float(
            getattr(
                candidate,
                "amount_in",
                0.0,
            )
        )

        gas_cost = float(
            getattr(
                candidate,
                "gas_cost",
                0.0,
            )
        )

        net_profit = float(
            getattr(
                candidate,
                "net_profit",
                0.0,
            )
        )

        profitable = bool(
            getattr(
                candidate,
                "profitable",
                False,
            )
        )

        # ----------------------------------------------------
        # Profitability
        # ----------------------------------------------------

        if self.limits.require_profitable and not profitable:
            reasons.append(
                "candidate is not profitable"
            )

        if net_profit < self.limits.min_net_profit_usd:
            reasons.append(
                "net profit is below minimum threshold"
            )

        # ----------------------------------------------------
        # Gas
        # ----------------------------------------------------

        if gas_cost > self.limits.max_gas_cost_usd:
            reasons.append(
                "gas cost exceeds configured maximum"
            )

        # ----------------------------------------------------
        # Trade size
        # ----------------------------------------------------

        if amount_in > self.limits.max_trade_size:
            reasons.append(
                "trade size exceeds configured maximum"
            )

        if amount_in > self.limits.max_position_size:
            reasons.append(
                "position size exceeds configured maximum"
            )

        # ----------------------------------------------------
        # Slippage
        # ----------------------------------------------------

        if slippage_percent < 0:
            reasons.append(
                "slippage cannot be negative"
            )

        elif slippage_percent > self.limits.max_slippage_percent:
            reasons.append(
                "slippage exceeds configured maximum"
            )

        # ----------------------------------------------------
        # Warnings
        # ----------------------------------------------------

        if net_profit < (
            self.limits.min_net_profit_usd * 2
        ):
            warnings.append(
                "profit is close to the minimum threshold"
            )

        if gas_cost > (
            self.limits.max_gas_cost_usd * 0.75
        ):
            warnings.append(
                "gas cost is close to the configured limit"
            )

        return RiskAssessment(
            approved=len(reasons) == 0,
            reasons=tuple(reasons),
            warnings=tuple(warnings),
        )