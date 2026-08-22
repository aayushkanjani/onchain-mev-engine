from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3

from .events import (
    V2_SWAP_TOPIC,
    V3_SWAP_TOPIC,
    SwapEvent,
    decode_v2_swap,
    decode_v3_swap,
)


# ============================================================
# KNOWN DEX FACTORIES / PROTOCOL IDENTIFIERS
# ============================================================

UNISWAP_V2_FACTORY = Web3.to_checksum_address(
    "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
)

UNISWAP_V3_FACTORY = Web3.to_checksum_address(
    "0x1F98431c8aD98523631AE4a59f267346ea31F984"
)


@dataclass(frozen=True)
class PoolMetadata:
    """
    Metadata required to interpret a pool swap.
    """

    address: str
    dex: str
    version: str

    token0: str
    token1: str

    fee: int | None = None
    tick_spacing: int | None = None


class SwapDetector:
    """
    Detect and normalize DEX swap events.

    This class intentionally does not try to infer arbitrary
    DEXes from transaction calldata.

    It works from known pool metadata.

    That gives us a deterministic foundation for:

        Ethereum logs
             ↓
        protocol event
             ↓
        normalized SwapEvent
    """

    def __init__(
        self,
        pools: dict[str, PoolMetadata] | None = None,
    ):
        self._pools: dict[str, PoolMetadata] = {}

        if pools:
            for pool in pools.values():
                self.register_pool(pool)

    # --------------------------------------------------------
    # Pool registration
    # --------------------------------------------------------

    def register_pool(
        self,
        pool: PoolMetadata,
    ) -> None:

        address = Web3.to_checksum_address(
            pool.address
        )

        self._pools[address.lower()] = pool

    def get_pool(
        self,
        address: str,
    ) -> PoolMetadata | None:

        return self._pools.get(
            address.lower()
        )

    # --------------------------------------------------------
    # Topic classification
    # --------------------------------------------------------

    @staticmethod
    def classify_log(
        log: dict[str, Any],
    ) -> str | None:

        topics = log.get("topics")

        if not topics:
            return None

        topic = topics[0]

        if hasattr(topic, "hex"):
            topic = topic.hex()

        topic = str(topic).lower()

        if topic == V2_SWAP_TOPIC.lower():
            return "V2"

        if topic == V3_SWAP_TOPIC.lower():
            return "V3"

        return None

    # --------------------------------------------------------
    # Decode one log
    # --------------------------------------------------------

    def decode_log(
        self,
        log: dict[str, Any],
    ) -> SwapEvent | None:

        version = self.classify_log(log)

        if version is None:
            return None

        pool_address = Web3.to_checksum_address(
            log["address"]
        )

        metadata = self.get_pool(
            pool_address
        )

        if metadata is None:
            return None

        if metadata.version != version:
            return None

        tx_hash = log.get(
            "transactionHash"
        )

        if tx_hash is not None:
            tx_hash = (
                tx_hash.hex()
                if hasattr(tx_hash, "hex")
                else str(tx_hash)
            )

        if version == "V2":

            return decode_v2_swap(
                log=log,
                tx_hash=tx_hash,
                token0=metadata.token0,
                token1=metadata.token1,
                dex=metadata.dex,
            )

        if version == "V3":

            return decode_v3_swap(
                log=log,
                tx_hash=tx_hash,
                token0=metadata.token0,
                token1=metadata.token1,
                dex=metadata.dex,
            )

        return None

    # --------------------------------------------------------
    # Decode transaction receipt
    # --------------------------------------------------------

    def detect_from_receipt(
        self,
        receipt: Any,
    ) -> list[SwapEvent]:

        events: list[SwapEvent] = []

        logs = (
            receipt["logs"]
            if isinstance(receipt, dict)
            else receipt.logs
        )

        for log in logs:

            event = self.decode_log(
                log
            )

            if event is not None:
                events.append(event)

        return sorted(
            events,
            key=lambda event: event.log_index,
        )

    # --------------------------------------------------------
    # Decode multiple receipts
    # --------------------------------------------------------

    def detect_from_receipts(
        self,
        receipts: list[Any],
    ) -> list[SwapEvent]:

        events: list[SwapEvent] = []

        for receipt in receipts:

            events.extend(
                self.detect_from_receipt(
                    receipt
                )
            )

        return sorted(
            events,
            key=lambda event: (
                event.block_number,
                event.tx_hash,
                event.log_index,
            ),
        )