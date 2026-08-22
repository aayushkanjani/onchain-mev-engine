from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionCost:
    """
    Costs associated with executing an arbitrage transaction.

    All monetary values are expressed in the same quote currency
    as the arbitrage PnL, typically USDC.
    """

    gas_used: int
    gas_price_gwei: float
    native_token_price: float

    @property
    def gas_cost_native(self) -> float:
        """
        Gas cost in the native token (ETH).

        gas_used * gas_price
        """
        return (
            self.gas_used
            * self.gas_price_gwei
            / 1_000_000_000
        )

    @property
    def gas_cost_usd(self) -> float:
        """Gas cost converted to the quote currency."""
        return (
            self.gas_cost_native
            * self.native_token_price
        )


@dataclass(frozen=True)
class ExecutionResult:
    gross_profit: float
    gas_cost: float
    net_profit: float

    profitable: bool


def evaluate_execution(
    gross_profit: float,
    execution_cost: ExecutionCost,
) -> ExecutionResult:
    """
    Determine whether an arbitrage remains profitable
    after gas costs.
    """

    gas_cost = execution_cost.gas_cost_usd

    net_profit = gross_profit - gas_cost

    return ExecutionResult(
        gross_profit=gross_profit,
        gas_cost=gas_cost,
        net_profit=net_profit,
        profitable=net_profit > 0,
    )