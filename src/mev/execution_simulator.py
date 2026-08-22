from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class SimulatedTrade:
    """
    Result of one simulated swap.

    The simulator never broadcasts a transaction.
    It only models the state transition locally.
    """

    token_in: str
    token_out: str
    amount_in: float
    amount_out: float


@dataclass(frozen=True)
class SimulationResult:
    """
    Result of a complete simulated execution sequence.
    """

    trades: list[SimulatedTrade]
    initial_balance: float
    final_balance: float
    gross_profit: float

    gas_cost: float
    net_profit: float

    profitable: bool


class ExecutionSimulator:
    """
    Local execution simulator for AMM-based strategies.

    The simulator works on copies of the supplied pools.

    Therefore:

        strategy
            ↓
        copied pool state
            ↓
        sequential swaps
            ↓
        final PnL

    The original pool objects are never mutated.
    """

    def __init__(
        self,
        gas_used: int = 250_000,
        gas_price_gwei: float = 20.0,
        native_token_price: float = 2_500.0,
    ):
        if gas_used <= 0:
            raise ValueError(
                "gas_used must be positive"
            )

        if gas_price_gwei < 0:
            raise ValueError(
                "gas_price_gwei must be non-negative"
            )

        if native_token_price <= 0:
            raise ValueError(
                "native_token_price must be positive"
            )

        self.gas_used = gas_used
        self.gas_price_gwei = gas_price_gwei
        self.native_token_price = native_token_price

    # ========================================================
    # GAS
    # ========================================================

    @property
    def gas_cost_native(self) -> float:
        """
        Return gas cost in the native token.
        """

        return (
            self.gas_used
            * self.gas_price_gwei
            / 1_000_000_000
        )

    @property
    def gas_cost_usd(self) -> float:
        """
        Return gas cost in USD.
        """

        return (
            self.gas_cost_native
            * self.native_token_price
        )

    # ========================================================
    # POOL COPY
    # ========================================================

    @staticmethod
    def clone_pool(pool: Any) -> Any:
        """
        Create an independent copy of a pool.

        This guarantees that execution simulation does not
        mutate market state.
        """

        return deepcopy(pool)

    # ========================================================
    # SINGLE SWAP
    # ========================================================

    @staticmethod
    def execute_swap(
        pool: Any,
        amount_in: float,
        token_in: str,
    ) -> SimulatedTrade:
        """
        Execute one swap against a simulated pool.

        The pool is expected to expose:

            get_amount_out()
            swap()
            token_x
            token_y
        """

        if amount_in <= 0:
            raise ValueError(
                "amount_in must be positive"
            )

        token_in_lower = token_in.lower()

        if token_in_lower == pool.token_x.lower():
            token_out = pool.token_y

        elif token_in_lower == pool.token_y.lower():
            token_out = pool.token_x

        else:
            raise ValueError(
                "token_in is not part of the pool"
            )

        amount_out = pool.swap(
            amount_in=amount_in,
            token_in=token_in,
        )

        return SimulatedTrade(
            token_in=token_in,
            token_out=token_out,
            amount_in=amount_in,
            amount_out=amount_out,
        )

    # ========================================================
    # SEQUENTIAL EXECUTION
    # ========================================================

    def simulate_sequence(
        self,
        pools: list[Any],
        trades: list[
            tuple[int, float, str]
        ],
        initial_balance: float,
    ) -> SimulationResult:
        """
        Simulate a sequence of swaps.

        Parameters
        ----------
        pools:
            Pool objects used by the strategy.

        trades:
            Tuples containing:

                (
                    pool_index,
                    amount_in,
                    token_in,
                )

        initial_balance:
            Starting balance in the strategy's quote currency.

        Example
        -------

            trades = [
                (0, 1000.0, "USDC"),
                (1, 0.5, "WETH"),
            ]

        Each pool is copied before execution.
        """

        if initial_balance <= 0:
            raise ValueError(
                "initial_balance must be positive"
            )

        simulated_pools = [
            self.clone_pool(pool)
            for pool in pools
        ]

        results: list[SimulatedTrade] = []

        current_balance = initial_balance

        for pool_index, amount_in, token_in in trades:

            if pool_index < 0:
                raise ValueError(
                    "pool_index must be non-negative"
                )

            if pool_index >= len(
                simulated_pools
            ):
                raise IndexError(
                    "pool_index is out of range"
                )

            trade = self.execute_swap(
                pool=simulated_pools[
                    pool_index
                ],
                amount_in=amount_in,
                token_in=token_in,
            )

            results.append(trade)

            current_balance = trade.amount_out

        gross_profit = (
            current_balance
            - initial_balance
        )

        net_profit = (
            gross_profit
            - self.gas_cost_usd
        )

        return SimulationResult(
            trades=results,
            initial_balance=initial_balance,
            final_balance=current_balance,
            gross_profit=gross_profit,
            gas_cost=self.gas_cost_usd,
            net_profit=net_profit,
            profitable=net_profit > 0,
        )

    # ========================================================
    # ARBITRAGE
    # ========================================================

    def simulate_arbitrage(
        self,
        buy_pool: Any,
        sell_pool: Any,
        amount_in: float,
        token_in: str,
    ) -> SimulationResult:
        """
        Simulate a two-pool arbitrage.

        Example:

            USDC
              ↓
          Buy pool
              ↓
            WETH
              ↓
          Sell pool
              ↓
            USDC
        """

        if amount_in <= 0:
            raise ValueError(
                "amount_in must be positive"
            )

        first_pool = self.clone_pool(
            buy_pool
        )

        second_pool = self.clone_pool(
            sell_pool
        )

        first_trade = self.execute_swap(
            pool=first_pool,
            amount_in=amount_in,
            token_in=token_in,
        )

        second_trade = self.execute_swap(
            pool=second_pool,
            amount_in=first_trade.amount_out,
            token_in=first_trade.token_out,
        )

        final_balance = (
            second_trade.amount_out
        )

        gross_profit = (
            final_balance
            - amount_in
        )

        net_profit = (
            gross_profit
            - self.gas_cost_usd
        )

        return SimulationResult(
            trades=[
                first_trade,
                second_trade,
            ],
            initial_balance=amount_in,
            final_balance=final_balance,
            gross_profit=gross_profit,
            gas_cost=self.gas_cost_usd,
            net_profit=net_profit,
            profitable=net_profit > 0,
        )

    # ========================================================
    # SANDWICH
    # ========================================================

    def simulate_sandwich(
        self,
        pool: Any,
        victim_amount_in: float,
        victim_token_in: str,
        attacker_amount_in: float,
    ) -> SimulationResult:
        """
        Simulate a sandwich around a victim transaction.

        Sequence:

            attacker front-run
                    ↓
            victim transaction
                    ↓
            attacker back-run

        The victim transaction is represented only by its
        swap amount and direction.

        This is a simulation model and does not construct or
        broadcast real transactions.
        """

        if victim_amount_in <= 0:
            raise ValueError(
                "victim_amount_in must be positive"
            )

        if attacker_amount_in <= 0:
            raise ValueError(
                "attacker_amount_in must be positive"
            )

        simulated_pool = self.clone_pool(
            pool
        )

        # ----------------------------------------------------
        # Front-run
        # ----------------------------------------------------

        front_run = self.execute_swap(
            pool=simulated_pool,
            amount_in=attacker_amount_in,
            token_in=victim_token_in,
        )

        # ----------------------------------------------------
        # Victim
        # ----------------------------------------------------

        victim = self.execute_swap(
            pool=simulated_pool,
            amount_in=victim_amount_in,
            token_in=victim_token_in,
        )

        # ----------------------------------------------------
        # Back-run
        # ----------------------------------------------------

        back_run = self.execute_swap(
            pool=simulated_pool,
            amount_in=front_run.amount_out,
            token_in=front_run.token_out,
        )

        final_balance = (
            back_run.amount_out
        )

        gross_profit = (
            final_balance
            - attacker_amount_in
        )

        net_profit = (
            gross_profit
            - self.gas_cost_usd
        )

        return SimulationResult(
            trades=[
                front_run,
                victim,
                back_run,
            ],
            initial_balance=attacker_amount_in,
            final_balance=final_balance,
            gross_profit=gross_profit,
            gas_cost=self.gas_cost_usd,
            net_profit=net_profit,
            profitable=net_profit > 0,
        )