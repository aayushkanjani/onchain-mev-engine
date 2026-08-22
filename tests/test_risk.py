from dataclasses import dataclass

import pytest

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


def test_profitable_candidate_is_approved():

    manager = RiskManager()

    candidate = FakeCandidate()

    result = manager.evaluate(
        candidate
    )

    assert result.approved is True
    assert result.rejected is False
    assert result.reasons == ()


def test_unprofitable_candidate_is_rejected():

    manager = RiskManager()

    candidate = FakeCandidate(
        profitable=False
    )

    result = manager.evaluate(
        candidate
    )

    assert result.approved is False

    assert (
        "candidate is not profitable"
        in result.reasons
    )


def test_low_profit_is_rejected():

    manager = RiskManager(
        RiskLimits(
            min_net_profit_usd=100.0
        )
    )

    candidate = FakeCandidate(
        net_profit=50.0
    )

    result = manager.evaluate(
        candidate
    )

    assert result.approved is False

    assert (
        "net profit is below minimum threshold"
        in result.reasons
    )


def test_high_gas_is_rejected():

    manager = RiskManager(
        RiskLimits(
            max_gas_cost_usd=10.0
        )
    )

    candidate = FakeCandidate(
        gas_cost=20.0
    )

    result = manager.evaluate(
        candidate
    )

    assert result.approved is False

    assert (
        "gas cost exceeds configured maximum"
        in result.reasons
    )


def test_large_trade_is_rejected():

    manager = RiskManager(
        RiskLimits(
            max_trade_size=5_000.0
        )
    )

    candidate = FakeCandidate(
        amount_in=10_000.0
    )

    result = manager.evaluate(
        candidate
    )

    assert result.approved is False

    assert (
        "trade size exceeds configured maximum"
        in result.reasons
    )


def test_high_slippage_is_rejected():

    manager = RiskManager(
        RiskLimits(
            max_slippage_percent=1.0
        )
    )

    candidate = FakeCandidate()

    result = manager.evaluate(
        candidate,
        slippage_percent=2.0,
    )

    assert result.approved is False

    assert (
        "slippage exceeds configured maximum"
        in result.reasons
    )


def test_negative_slippage_is_rejected():

    manager = RiskManager()

    candidate = FakeCandidate()

    result = manager.evaluate(
        candidate,
        slippage_percent=-1.0,
    )

    assert result.approved is False

    assert (
        "slippage cannot be negative"
        in result.reasons
    )


def test_invalid_limits():

    with pytest.raises(
        ValueError
    ):
        RiskManager(
            RiskLimits(
                max_trade_size=0
            )
        )