from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from web3 import Web3


# ============================================================
# EVENT SIGNATURES
# ============================================================

TRANSFER_TOPIC = Web3.keccak(
    text="Transfer(address,address,uint256)"
).hex()

V2_SWAP_TOPIC = Web3.keccak(
    text="Swap(address,uint256,uint256,uint256,uint256,address)"
).hex()

V3_SWAP_TOPIC = Web3.keccak(
    text="Swap(address,address,int256,int256,uint160,uint128,int24)"
).hex()


# ============================================================
# NORMALIZED SWAP EVENT
# ============================================================

@dataclass(frozen=True)
class SwapEvent:
    """
    Protocol-independent representation of a DEX swap.

    All raw token amounts are kept as integers.

    token0/token1 are the pool's canonical token ordering.

    amount0 and amount1 follow the native Uniswap event
    semantics:

        positive  -> tokens sent to the pool
        negative  -> tokens received from the pool

    This allows V2 and V3 swaps to be represented uniformly.
    """

    tx_hash: str
    block_number: int
    log_index: int

    dex: str
    version: str

    pool_address: str
    sender: str
    recipient: str

    token0: str
    token1: str

    amount0: int
    amount1: int

    sqrt_price_x96: int | None = None
    liquidity: int | None = None
    tick: int | None = None

    @property
    def token_in(self) -> str:
        """
        Return the token sent into the pool.

        For Uniswap event semantics, the positive
        amount identifies the input token.
        """

        if self.amount0 > 0:
            return self.token0

        if self.amount1 > 0:
            return self.token1

        raise ValueError(
            "Swap event has no positive input amount"
        )

    @property
    def token_out(self) -> str:
        """
        Return the token received from the pool.
        """

        if self.amount0 < 0:
            return self.token0

        if self.amount1 < 0:
            return self.token1

        raise ValueError(
            "Swap event has no negative output amount"
        )

    @property
    def amount_in(self) -> int:
        """
        Absolute raw amount entering the pool.
        """

        if self.amount0 > 0:
            return self.amount0

        if self.amount1 > 0:
            return self.amount1

        raise ValueError(
            "Swap event has no positive input amount"
        )

    @property
    def amount_out(self) -> int:
        """
        Absolute raw amount leaving the pool.
        """

        if self.amount0 < 0:
            return -self.amount0

        if self.amount1 < 0:
            return -self.amount1

        raise ValueError(
            "Swap event has no negative output amount"
        )


# ============================================================
# HELPERS
# ============================================================

def _topic_hex(topic: Any) -> str:
    """
    Normalize a Web3 topic into a lowercase hex string.
    """

    if hasattr(topic, "hex"):
        return topic.hex().lower()

    return str(topic).lower()


def _address_from_topic(topic: Any) -> str:
    """
    Decode an indexed Ethereum address from a topic.
    """

    value = _topic_hex(topic)

    return Web3.to_checksum_address(
        "0x" + value[-40:]
    )


def _data_bytes(log: dict[str, Any]) -> bytes:
    """
    Normalize log data into bytes.
    """

    data = log["data"]

    if isinstance(data, bytes):
        return data

    if hasattr(data, "hex") and not isinstance(data, str):
        return bytes(data)

    if isinstance(data, str):
        return bytes.fromhex(
            data.removeprefix("0x")
        )

    return bytes(data)


def _decode_uint256(value: bytes) -> int:
    return int.from_bytes(
        value,
        byteorder="big",
        signed=False,
    )


def _decode_int256(value: bytes) -> int:
    return int.from_bytes(
        value,
        byteorder="big",
        signed=True,
    )


def _word(data: bytes, index: int) -> bytes:
    start = index * 32
    end = start + 32

    if len(data) < end:
        raise ValueError(
            "Malformed event data"
        )

    return data[start:end]


# ============================================================
# UNISWAP V2
# ============================================================

def decode_v2_swap(
    log: dict[str, Any],
    tx_hash: str | None = None,
    token0: str | None = None,
    token1: str | None = None,
    dex: str = "Uniswap",
) -> SwapEvent | None:
    """
    Decode a Uniswap V2-style Swap event.

    Event:

        Swap(
            address indexed sender,
            uint amount0In,
            uint amount1In,
            uint amount0Out,
            uint amount1Out,
            address indexed to
        )
    """

    topics = log["topics"]

    if not topics:
        return None

    if _topic_hex(topics[0]) != V2_SWAP_TOPIC:
        return None

    if token0 is None or token1 is None:
        raise ValueError(
            "token0 and token1 are required "
            "for normalized V2 swap decoding"
        )

    if len(topics) < 3:
        raise ValueError(
            "Malformed V2 Swap event"
        )

    data = _data_bytes(log)

    amount0_in = _decode_uint256(
        _word(data, 0)
    )

    amount1_in = _decode_uint256(
        _word(data, 1)
    )

    amount0_out = _decode_uint256(
        _word(data, 2)
    )

    amount1_out = _decode_uint256(
        _word(data, 3)
    )

    amount0 = (
        amount0_in
        - amount0_out
    )

    amount1 = (
        amount1_in
        - amount1_out
    )

    return SwapEvent(
        tx_hash=(
            tx_hash
            or str(log.get("transactionHash"))
        ),
        block_number=int(
            log["blockNumber"]
        ),
        log_index=int(
            log["logIndex"]
        ),
        dex=dex,
        version="V2",
        pool_address=Web3.to_checksum_address(
            log["address"]
        ),
        sender=_address_from_topic(
            topics[1]
        ),
        recipient=_address_from_topic(
            topics[2]
        ),
        token0=Web3.to_checksum_address(
            token0
        ),
        token1=Web3.to_checksum_address(
            token1
        ),
        amount0=amount0,
        amount1=amount1,
    )


# ============================================================
# UNISWAP V3
# ============================================================

def decode_v3_swap(
    log: dict[str, Any],
    tx_hash: str | None = None,
    token0: str | None = None,
    token1: str | None = None,
    dex: str = "Uniswap",
) -> SwapEvent | None:
    """
    Decode a Uniswap V3 Swap event.

    Event:

        Swap(
            address indexed sender,
            address indexed recipient,
            int256 amount0,
            int256 amount1,
            uint160 sqrtPriceX96,
            uint128 liquidity,
            int24 tick
        )
    """

    topics = log["topics"]

    if not topics:
        return None

    if _topic_hex(topics[0]) != V3_SWAP_TOPIC:
        return None

    if token0 is None or token1 is None:
        raise ValueError(
            "token0 and token1 are required "
            "for normalized V3 swap decoding"
        )

    if len(topics) < 3:
        raise ValueError(
            "Malformed V3 Swap event"
        )

    data = _data_bytes(log)

    amount0 = _decode_int256(
        _word(data, 0)
    )

    amount1 = _decode_int256(
        _word(data, 1)
    )

    sqrt_price_x96 = _decode_uint256(
        _word(data, 2)
    )

    liquidity = _decode_uint256(
        _word(data, 3)
    )

    tick = _decode_int256(
        _word(data, 4)
    )

    return SwapEvent(
        tx_hash=(
            tx_hash
            or str(log.get("transactionHash"))
        ),
        block_number=int(
            log["blockNumber"]
        ),
        log_index=int(
            log["logIndex"]
        ),
        dex=dex,
        version="V3",
        pool_address=Web3.to_checksum_address(
            log["address"]
        ),
        sender=_address_from_topic(
            topics[1]
        ),
        recipient=_address_from_topic(
            topics[2]
        ),
        token0=Web3.to_checksum_address(
            token0
        ),
        token1=Web3.to_checksum_address(
            token1
        ),
        amount0=amount0,
        amount1=amount1,
        sqrt_price_x96=sqrt_price_x96,
        liquidity=liquidity,
        tick=tick,
    )


# ============================================================
# TRANSFER DECODER
# ============================================================

def decode_transfer(
    log: dict[str, Any],
    decimals: int | None = None,
):
    """
    Decode an ERC-20 Transfer event.

    Kept for compatibility with the existing
    transaction-analysis layer.
    """

    topics = log["topics"]

    if not topics:
        return None

    if _topic_hex(topics[0]) != TRANSFER_TOPIC:
        return None

    if len(topics) < 3:
        raise ValueError(
            "Malformed Transfer event"
        )

    from_address = _address_from_topic(
        topics[1]
    )

    to_address = _address_from_topic(
        topics[2]
    )

    raw_value = _decode_uint256(
        _data_bytes(log)
    )

    result = {
        "from": from_address,
        "to": to_address,
        "raw_value": raw_value,
    }

    if decimals is not None:
        result["value"] = (
            raw_value
            / (10 ** decimals)
        )

    return result