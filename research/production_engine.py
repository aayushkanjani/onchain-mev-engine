from __future__ import annotations

import asyncio

from src.blockchain.client import EthereumClient
from src.production.engine import ProductionEngine


async def main():
    print("=" * 70)
    print("ON-CHAIN MEV ENGINE — PRODUCTION ARCHITECTURE")
    print("=" * 70)

    client = EthereumClient()

    # The existing EthereumClient internally manages the RPC
    # connection. We use its Web3 instance for BlockScanner.
    web3 = client.web3

    engine = ProductionEngine(
        web3=web3,
        client=client,
        database_path="data/market_state.db",
        poll_interval=1.0,
        queue_size=10_000,
        max_retries=3,
        retry_delay=0.5,
    )

    latest_block = await engine.stream.latest_block()

    print()
    print(
        f"Latest block: {latest_block}"
    )

    print()
    print(
        "Starting production engine..."
    )

    print(
        "Processing one block for the milestone demo."
    )

    await engine.run(
        start_block=latest_block,
        max_blocks=1,
    )

    snapshot = engine.metrics.snapshot()

    print()
    print("-" * 70)
    print("METRICS")
    print("-" * 70)

    print(
        f"Blocks processed: "
        f"{snapshot.blocks_processed}"
    )

    print(
        f"Swaps detected:   "
        f"{snapshot.swaps_detected}"
    )

    print(
        f"Failures:         "
        f"{snapshot.failures}"
    )

    print(
        f"Last latency:     "
        f"{snapshot.last_latency_ms:.2f} ms"
    )

    print(
        f"Average latency:  "
        f"{snapshot.average_latency_ms:.2f} ms"
    )

    print()
    print("-" * 70)

    latest_processed = (
        engine.state.latest_processed_block()
    )

    print(
        f"Persisted block: "
        f"{latest_processed}"
    )

    print(
        f"Queue size:      "
        f"{engine.opportunity_queue.qsize()}"
    )

    print()
    print(
        "Production architecture test complete."
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )