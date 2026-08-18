from dataclasses import dataclass

from src.amm.pool import AMMPool


@dataclass
class ArbitrageResult:
    """
    Result of an arbitrage simulation.
    """

    amount_in: float
    intermediate_amount: float
    final_amount: float
    profit: float

    @property
    def profitable(self) -> bool:
        return self.profit > 0


def simulate_arbitrage(
    buy_pool: AMMPool,
    sell_pool: AMMPool,
    amount_in: float,
) -> ArbitrageResult:
    """
    Simulate:

        USDC
          ↓
       Buy ETH
          ↓
       Sell ETH
          ↓
        USDC

    The pools are NOT modified.
    """

    # Buy ETH from the cheaper pool.
    eth_received = buy_pool.get_amount_out(
        amount_in=amount_in,
        token_in="USDC",
    )

    # Sell ETH in the more expensive pool.
    usdc_received = sell_pool.get_amount_out(
        amount_in=eth_received,
        token_in="ETH",
    )

    profit = usdc_received - amount_in

    return ArbitrageResult(
        amount_in=amount_in,
        intermediate_amount=eth_received,
        final_amount=usdc_received,
        profit=profit,
    )