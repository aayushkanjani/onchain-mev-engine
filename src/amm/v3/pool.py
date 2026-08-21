from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .swap import compute_swap_step
from .tick import (
    MAX_TICK,
    MIN_TICK,
    TickInfo,
    get_sqrt_ratio_at_tick,
    compress_tick,
    position,
)


@dataclass
class V3SwapResult:
    amount_in: int
    amount_out: int
    fee_amount: int

    sqrt_price_before: int
    sqrt_price_after: int

    tick_before: int
    tick_after: int

    ticks_crossed: list[int]


@dataclass
class V3Pool:
    token0: str
    token1: str

    sqrt_price_x96: int
    tick: int
    liquidity: int

    fee: int
    tick_spacing: int

    # Local initialized ticks for deterministic tests.
    initialized_ticks: list[TickInfo] | None = None

    # Optional real on-chain providers.
    bitmap_provider: Callable[[int], int] | None = None
    tick_provider: Callable[[int], TickInfo] | None = None

    # ------------------------------------------------------------------
    # LOCAL TICK SEARCH
    # ------------------------------------------------------------------

    def _local_next_tick(
        self,
        current_tick: int,
        zero_for_one: bool,
    ) -> TickInfo | None:

        if not self.initialized_ticks:
            return None

        if zero_for_one:

            # Moving price downward.
            #
            # IMPORTANT:
            # The next tick must be STRICTLY below the
            # current tick. Otherwise, after crossing tick X,
            # we would find X again forever.
            candidates = [
                tick
                for tick in self.initialized_ticks
                if tick.tick < current_tick
            ]

            if not candidates:
                return None

            return max(
                candidates,
                key=lambda x: x.tick,
            )

        # Moving price upward.
        #
        # The next initialized tick must be strictly above
        # the current tick.
        candidates = [
            tick
            for tick in self.initialized_ticks
            if tick.tick > current_tick
        ]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda x: x.tick,
        )

    # ------------------------------------------------------------------
    # ON-CHAIN BITMAP SEARCH
    # ------------------------------------------------------------------

    def _bitmap_next_tick(
        self,
        current_tick: int,
        zero_for_one: bool,
    ) -> TickInfo | None:

        if (
            self.bitmap_provider is None
            or self.tick_provider is None
        ):
            return None

        compressed = compress_tick(
            current_tick,
            self.tick_spacing,
        )

        # ==============================================================
        # zeroForOne
        #
        # Search strictly BELOW the current compressed tick.
        # ==============================================================

        if zero_for_one:

            compressed -= 1

            min_compressed = (
                MIN_TICK // self.tick_spacing
            )

            while compressed >= min_compressed:

                word_position, bit_position = position(
                    compressed
                )

                word = self.bitmap_provider(
                    word_position
                )

                # Include bit_position and everything below it.
                mask = (
                    (1 << (bit_position + 1))
                    - 1
                )

                masked = word & mask

                if masked:

                    highest_bit = (
                        masked.bit_length() - 1
                    )

                    next_compressed = (
                        (word_position << 8)
                        + highest_bit
                    )

                    next_tick = (
                        next_compressed
                        * self.tick_spacing
                    )

                    return self.tick_provider(
                        next_tick
                    )

                # Move to previous 256-bit word.
                compressed = (
                    (word_position << 8) - 1
                )

            return None

        # ==============================================================
        # oneForZero
        #
        # Search strictly ABOVE the current compressed tick.
        # ==============================================================

        compressed += 1

        max_compressed = (
            MAX_TICK // self.tick_spacing
        )

        while compressed <= max_compressed:

            word_position, bit_position = position(
                compressed
            )

            word = self.bitmap_provider(
                word_position
            )

            if bit_position == 255:

                masked = 0

            else:

                # Keep only bits strictly above bit_position.
                mask = (
                    ~(
                        (1 << (bit_position + 1))
                        - 1
                    )
                ) & ((1 << 256) - 1)

                masked = word & mask

            if masked:

                lowest_bit = (
                    masked & -masked
                ).bit_length() - 1

                next_compressed = (
                    (word_position << 8)
                    + lowest_bit
                )

                next_tick = (
                    next_compressed
                    * self.tick_spacing
                )

                return self.tick_provider(
                    next_tick
                )

            # Move to next bitmap word.
            compressed = (
                (word_position + 1) << 8
            )

        return None

    # ------------------------------------------------------------------
    # NEXT TICK
    # ------------------------------------------------------------------

    def _next_tick(
        self,
        current_tick: int,
        zero_for_one: bool,
    ) -> TickInfo | None:

        # Prefer real on-chain data.
        if (
            self.bitmap_provider is not None
            and self.tick_provider is not None
        ):

            return self._bitmap_next_tick(
                current_tick,
                zero_for_one,
            )

        # Deterministic local implementation for tests.
        return self._local_next_tick(
            current_tick,
            zero_for_one,
        )

    # ------------------------------------------------------------------
    # SWAP
    # ------------------------------------------------------------------

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

        ticks_crossed: list[int] = []

        sqrt_price_before = sqrt_price
        tick_before = current_tick

        # --------------------------------------------------------------
        # Swap loop
        # --------------------------------------------------------------

        while remaining > 0:

            next_tick = self._next_tick(
                current_tick,
                zero_for_one,
            )

            # ----------------------------------------------------------
            # Determine target price.
            # ----------------------------------------------------------

            if next_tick is None:

                target_tick = (
                    MIN_TICK
                    if zero_for_one
                    else MAX_TICK
                )

                target_sqrt_price = (
                    get_sqrt_ratio_at_tick(
                        target_tick
                    )
                )

            else:

                target_tick = next_tick.tick

                target_sqrt_price = (
                    get_sqrt_ratio_at_tick(
                        target_tick
                    )
                )

            # ----------------------------------------------------------
            # Execute one V3 swap step.
            # ----------------------------------------------------------

            step = compute_swap_step(
                sqrt_price_current=sqrt_price,
                sqrt_price_target=target_sqrt_price,
                liquidity=current_liquidity,
                amount_remaining=remaining,
                fee_pips=self.fee,
            )

            # ----------------------------------------------------------
            # Update price.
            # ----------------------------------------------------------

            previous_sqrt_price = sqrt_price

            sqrt_price = step.sqrt_price_next

            # ----------------------------------------------------------
            # Update amounts.
            # ----------------------------------------------------------

            consumed = (
                step.amount_in
                + step.fee_amount
            )

            if consumed <= 0:

                raise RuntimeError(
                    "V3 swap made no progress: "
                    f"remaining={remaining}, "
                    f"sqrt_price={sqrt_price}, "
                    f"target={target_sqrt_price}, "
                    f"liquidity={current_liquidity}"
                )

            remaining -= consumed

            amount_out_total += step.amount_out
            fee_total += step.fee_amount

            # ----------------------------------------------------------
            # Safety invariant.
            #
            # Price must change whenever we consume input.
            # ----------------------------------------------------------

            if sqrt_price == previous_sqrt_price:

                raise RuntimeError(
                    "V3 swap consumed input without "
                    "changing sqrt price"
                )

            # ----------------------------------------------------------
            # Did we reach the target tick?
            # ----------------------------------------------------------

            reached_target = (
                sqrt_price == target_sqrt_price
            )

            if not reached_target:

                # The current liquidity interval was enough
                # to consume the remaining input.
                #
                # We stop because there is no tick crossing.
                break

            # ----------------------------------------------------------
            # No initialized tick exists.
            #
            # We reached the global boundary.
            # ----------------------------------------------------------

            if next_tick is None:

                current_tick = target_tick

                break

            # ----------------------------------------------------------
            # CROSS INITIALIZED TICK
            # ----------------------------------------------------------

            crossed_tick = next_tick.tick

            # Move the current tick to the boundary we crossed.
            current_tick = crossed_tick

            # ----------------------------------------------------------
            # IMPORTANT:
            #
            # liquidityNet describes the net liquidity change
            # when crossing the tick from left → right.
            #
            # Therefore:
            #
            # zeroForOne (right → left):
            #     L -= liquidityNet
            #
            # oneForZero (left → right):
            #     L += liquidityNet
            # ----------------------------------------------------------

            if zero_for_one:

                current_liquidity -= (
                    next_tick.liquidity_net
                )

            else:

                current_liquidity += (
                    next_tick.liquidity_net
                )

            if current_liquidity <= 0:

                raise ValueError(
                    "Liquidity became non-positive "
                    f"after crossing tick {crossed_tick}"
                )

            ticks_crossed.append(
                crossed_tick
            )

        # --------------------------------------------------------------
        # Final result
        # --------------------------------------------------------------

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