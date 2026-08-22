from dataclasses import dataclass

from src.mev.execution_gate import (
    ExecutionGate,
)
from src.mev.risk import (
    RiskLimits,
    RiskManager,
)


@dataclass
class FakeCandidate:

    strategy: str = "arbitrage"
    amount_in: float = 10_000.0
    gas_cost: float = 12.5
    net_profit: float = 100.0
    profitable: bool = True


def test_execution_gate_approves_safe_candidate():

    manager = RiskManager(
        RiskLimits(
            min_net_profit_usd=25.0,
            max_gas_cost_usd=100.0,
            max_trade_size=100_000.0,
            max_slippage_percent=1.0,
        )
    )

    gate = ExecutionGate(
        manager
    )

    decision = gate.evaluate(
        FakeCandidate(),
        slippage_percent=0.25,
    )

    assert decision.approved is True
    assert decision.action == "APPROVE"
    assert decision.strategy == "arbitrage"


def test_execution_gate_rejects_risky_candidate():

    manager = RiskManager(
        RiskLimits(
            min_net_profit_usd=25.0
        )
    )

    gate = ExecutionGate(
        manager
    )

    candidate = FakeCandidate(
        net_profit=5.0
    )

    decision = gate.evaluate(
        candidate
    )

    assert decision.approved is False
    assert decision.action == "REJECT"

    assert (
        "net profit is below minimum threshold"
        in decision.risk.reasons
    )


def test_execution_gate_preserves_profit():

    manager = RiskManager()

    gate = ExecutionGate(
        manager
    )

    candidate = FakeCandidate(
        net_profit=123.45
    )

    decision = gate.evaluate(
        candidate
    )

    assert decision.net_profit == 123.45