from __future__ import annotations

from src.amm.v3.tick import TickInfo


class OnChainV3TickProvider:

    def __init__(self, pool):
        self.pool = pool

    def bitmap(self, word_position: int) -> int:

        return self.pool.tick_bitmap(
            word_position
        )

    def tick(self, tick: int) -> TickInfo:

        data = self.pool.ticks(tick)

        # ABI ordering:
        #
        # liquidityGross
        # liquidityNet
        # feeGrowthOutside0X128
        # ...
        #
        liquidity_net = int(data[1])

        return TickInfo(
            tick=tick,
            liquidity_net=liquidity_net,
        )