from __future__ import annotations

from dataclasses import dataclass

from .risk import (
    RiskAssessment,
    RiskManager,
)


@dataclass(frozen=True)
class ExecutionDecision:
    """
    Final decision produced by the execution gate.

    No transaction is signed or broadcast.

    action can be:

        APPROVE
        REJECT
    """

    action: str
    strategy: str
    amount_in: float
    net_profit: float
    risk: RiskAssessment

    @property
    def approved(self) -> bool:
        return self.action == "APPROVE"


class ExecutionGate:
    """
    Final safety barrier between strategy evaluation and
    paper execution.

    Architecture:

        Strategy
           ↓
        Candidate
           ↓
        RiskManager
           ↓
        ExecutionGate
           ↓
        ExecutionDecision

    The gate deliberately contains no private key,
    transaction signing, nonce management, or broadcast logic.
    """

    def __init__(
        self,
        risk_manager: RiskManager,
    ) -> None:

        self.risk_manager = risk_manager

    def evaluate(
        self,
        candidate,
        slippage_percent: float = 0.0,
    ) -> ExecutionDecision:
        """
        Produce a final execution decision.
        """

        risk = self.risk_manager.evaluate(
            candidate=candidate,
            slippage_percent=slippage_percent,
        )

        strategy = getattr(
            candidate,
            "strategy",
            "unknown",
        )

        if hasattr(
            strategy,
            "value",
        ):
            strategy = strategy.value

        strategy = str(strategy)

        amount_in = float(
            getattr(
                candidate,
                "amount_in",
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

        action = (
            "APPROVE"
            if risk.approved
            else "REJECT"
        )

        return ExecutionDecision(
            action=action,
            strategy=strategy,
            amount_in=amount_in,
            net_profit=net_profit,
            risk=risk,
        )