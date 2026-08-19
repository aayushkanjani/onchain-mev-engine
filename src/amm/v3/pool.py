from dataclasses import dataclass
from typing import List

from .swap import compute_swap_step
from .tick import get_sqrt_ratio_at_tick


@dataclass
class InitializedTick:

    tick: int
    liquidity_net: int


@dataclass
class V3SwapResult:

    amount_in: int
    amount_out: int

    fee_amount: int

    sqrt_price_before: int
    sqrt_price_after: int

    tick_before: int
    tick_after: int

    ticks_crossed: List[int]


@dataclass
class V3Pool:

    token0: str
    token1: str

    sqrt_price_x96: int
    tick: int
    liquidity: int

    fee: int
    tick_spacing: int

    initialized_ticks: List[InitializedTick]

    def _next_tick(
        self,
        current_tick: int,
        zero_for_one: bool,
    ):

        if zero_for_one:

            candidates = [
                t
                for t in self.initialized_ticks
                if t.tick <= current_tick
            ]

            if not candidates:
                return None

            return max(
                candidates,
                key=lambda t: t.tick,
            )

        candidates = [
            t
            for t in self.initialized_ticks
            if t.tick > current_tick
        ]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda t: t.tick,
        )

    def swap_exact_input(
        self,
        amount_in: int,
        zero_for_one: bool,
    ) -> V3SwapResult:

        if amount_in <= 0:
            raise ValueError(
                "amount_in must be positive"
            )

        remaining = amount_in

        sqrt_price = self.sqrt_price_x96
        current_tick = self.tick
        current_liquidity = self.liquidity

        amount_out_total = 0
        fee_total = 0

        ticks_crossed = []

        sqrt_price_before = sqrt_price
        tick_before = current_tick

        while remaining > 0:

            next_tick = self._next_tick(
                current_tick,
                zero_for_one,
            )

            if next_tick is None:
                break

            target_sqrt_price = (
                get_sqrt_ratio_at_tick(
                    next_tick.tick
                )
            )

            step = compute_swap_step(
                sqrt_price_current=sqrt_price,
                sqrt_price_target=target_sqrt_price,
                liquidity=current_liquidity,
                amount_remaining=remaining,
                fee_pips=self.fee,
            )

            sqrt_price = step.sqrt_price_next

            remaining -= (
                step.amount_in
                + step.fee_amount
            )

            amount_out_total += (
                step.amount_out
            )

            fee_total += step.fee_amount

            reached_tick = (
                sqrt_price
                == target_sqrt_price
            )

            if reached_tick:

                current_tick = (
                    next_tick.tick
                )

                current_liquidity += (
                    next_tick.liquidity_net
                    if zero_for_one
                    else -next_tick.liquidity_net
                )

                if current_liquidity <= 0:
                    raise ValueError(
                        "Liquidity became non-positive"
                    )

                ticks_crossed.append(
                    next_tick.tick
                )

            else:

                break

        return V3SwapResult(
            amount_in=amount_in - remaining,
            amount_out=amount_out_total,
            fee_amount=fee_total,
            sqrt_price_before=sqrt_price_before,
            sqrt_price_after=sqrt_price,
            tick_before=tick_before,
            tick_after=current_tick,
            ticks_crossed=ticks_crossed,
        )