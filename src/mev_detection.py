from __future__ import annotations

from src.blockchain.client import EthereumClient
from src.blockchain.swap_detection import (
    PoolMetadata,
    SwapDetector,
)


# ============================================================
# KNOWN UNISWAP V3 POOL
# ============================================================

WETH_USDC_V3 = (
    "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"
)

USDC = (
    "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
)

WETH = (
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
)


def create_detector() -> SwapDetector:

    detector = SwapDetector()

    detector.register_pool(
        PoolMetadata(
            address=WETH_USDC_V3,
            dex="Uniswap",
            version="V3",
            token0=USDC,
            token1=WETH,
            fee=500,
            tick_spacing=10,
        )
    )

    return detector


def main():

    client = EthereumClient()

    detector = create_detector()

    latest_block = client.latest_block()

    print("=" * 70)
    print("MEV DETECTION — SWAP DISCOVERY")
    print("=" * 70)

    print()
    print(
        f"Latest block: {latest_block}"
    )

    # --------------------------------------------------------
    # Analyze the latest block.
    #
    # We deliberately keep this to one block for now.
    # --------------------------------------------------------

    print()
    print(
        f"Analyzing block {latest_block}..."
    )

    block = client.get_block(
        latest_block,
        full_transactions=True,
    )

    print(
        f"Transactions: "
        f"{len(block['transactions'])}"
    )

    receipts = client.get_block_receipts(
        latest_block
    )

    events = detector.detect_from_receipts(
        receipts
    )

    print()
    print(
        f"Detected Uniswap swaps: "
        f"{len(events)}"
    )

    print()
    print("-" * 70)

    for event in events:

        print(
            f"TX:       {event.tx_hash}"
        )

        print(
            f"DEX:      {event.dex} {event.version}"
        )

        print(
            f"Pool:     {event.pool_address}"
        )

        print(
            f"Token in: {event.token_in}"
        )

        print(
            f"Token out:{event.token_out}"
        )

        print(
            f"Amount in:{event.amount_in}"
        )

        print(
            f"Amount out:{event.amount_out}"
        )

        if event.version == "V3":

            print(
                f"Tick:     {event.tick}"
            )

            print(
                f"Liquidity:{event.liquidity}"
            )

        print(
            f"Log:      {event.log_index}"
        )

        print("-" * 70)


if __name__ == "__main__":
    main()