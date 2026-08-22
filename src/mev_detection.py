from __future__ import annotations

from src.blockchain.swap_detection import (
    PoolMetadata,
    SwapDetector,
)


# ============================================================
# TOKENS
# ============================================================

USDC = (
    "0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
)

WETH = (
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
)


# ============================================================
# UNISWAP POOLS
# ============================================================

# Uniswap V2 WETH/USDC
WETH_USDC_V2 = (
    "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
)

# Uniswap V3 WETH/USDC 0.05%
WETH_USDC_V3 = (
    "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"
)


# ============================================================
# DETECTOR FACTORY
# ============================================================

def create_detector() -> SwapDetector:
    """
    Create the production swap detector.

    Milestone 10 registers two WETH/USDC pools:

        Uniswap V2
             +
        Uniswap V3

    This gives the opportunity engine multiple venues
    from which to detect price discrepancies.
    """

    detector = SwapDetector()

    # --------------------------------------------------------
    # Uniswap V2
    # --------------------------------------------------------

    detector.register_pool(
        PoolMetadata(
            address=WETH_USDC_V2,
            dex="Uniswap",
            version="V2",
            token0=USDC,
            token1=WETH,
        )
    )

    # --------------------------------------------------------
    # Uniswap V3
    # --------------------------------------------------------

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


def main() -> None:
    """
    Print the configured MEV pools.
    """

    detector = create_detector()

    print("=" * 70)
    print("MEV DETECTION — REGISTERED POOLS")
    print("=" * 70)

    print()

    for address in detector.pool_addresses():

        pool = detector.get_pool(
            address
        )

        if pool is None:
            continue

        print(
            f"DEX:      {pool.dex}"
        )

        print(
            f"Version:  {pool.version}"
        )

        print(
            f"Pool:     {pool.address}"
        )

        print(
            f"Token0:   {pool.token0}"
        )

        print(
            f"Token1:   {pool.token1}"
        )

        if pool.fee is not None:

            print(
                f"Fee:      {pool.fee}"
            )

        print(
            "-" * 70
        )


if __name__ == "__main__":
    main()