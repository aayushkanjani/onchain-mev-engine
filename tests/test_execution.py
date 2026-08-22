from src.amm.execution import (
    ExecutionCost,
    evaluate_execution,
)


def test_gas_cost():

    cost = ExecutionCost(
        gas_used=250_000,
        gas_price_gwei=20,
        native_token_price=2_500,
    )

    assert cost.gas_cost_native == 0.005
    assert cost.gas_cost_usd == 12.5


def test_profitable_execution():

    cost = ExecutionCost(
        gas_used=250_000,
        gas_price_gwei=20,
        native_token_price=2_500,
    )

    result = evaluate_execution(
        gross_profit=100,
        execution_cost=cost,
    )

    assert result.gas_cost == 12.5
    assert result.net_profit == 87.5
    assert result.profitable


def test_unprofitable_execution():

    cost = ExecutionCost(
        gas_used=250_000,
        gas_price_gwei=20,
        native_token_price=2_500,
    )

    result = evaluate_execution(
        gross_profit=10,
        execution_cost=cost,
    )

    assert result.net_profit == -2.5
    assert not result.profitable