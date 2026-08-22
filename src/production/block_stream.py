from __future__ import annotations

import asyncio
from typing import AsyncIterator


class BlockStream:
    """
    Asynchronous Ethereum block stream.

    The stream polls the Ethereum RPC for the latest block and
    yields every newly available block in order.

    This intentionally uses polling instead of WebSocket subscriptions
    so the architecture works with the existing EthereumClient.
    """

    def __init__(
        self,
        client,
        poll_interval: float = 1.0,
    ):
        if poll_interval <= 0:
            raise ValueError(
                "poll_interval must be positive"
            )

        self.client = client
        self.poll_interval = poll_interval

    async def latest_block(self) -> int:
        """
        Retrieve the latest block asynchronously.
        """

        return await asyncio.to_thread(
            self.client.latest_block
        )

    async def stream(
        self,
        start_block: int | None = None,
    ) -> AsyncIterator[int]:
        """
        Continuously yield newly mined Ethereum blocks.

        Parameters
        ----------
        start_block:
            Block from which streaming should begin.

            If None, start from the current latest block.

        Yields
        ------
        int
            Newly available block numbers.
        """

        if start_block is None:
            current_block = await self.latest_block()
        else:
            if start_block < 0:
                raise ValueError(
                    "start_block must be non-negative"
                )

            current_block = start_block - 1

        while True:
            latest = await self.latest_block()

            while current_block < latest:
                current_block += 1
                yield current_block

            await asyncio.sleep(
                self.poll_interval
            )