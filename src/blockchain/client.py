from __future__ import annotations

import os
from typing import Any, Iterable

from dotenv import load_dotenv
from web3 import Web3


load_dotenv()


class EthereumClient:
    """
    Ethereum RPC client.

    Responsibilities:

        RPC provider
            ↓
        blocks
        transactions
        receipts
        logs
        gas data

    MEV/business logic should remain outside this class.
    """

    def __init__(
        self,
        rpc_url: str | None = None,
    ):
        rpc_url = (
            rpc_url
            or os.getenv("ETH_RPC_URL")
        )

        if not rpc_url:
            raise ValueError(
                "ETH_RPC_URL is not set. "
                "Add it to the .env file."
            )

        self.rpc_url = rpc_url

        self.w3 = Web3(
            Web3.HTTPProvider(
                rpc_url
            )
        )

        if not self.w3.is_connected():
            raise ConnectionError(
                "Could not connect to Ethereum RPC. "
                "Check ETH_RPC_URL."
            )
            
    @property
    def web3(self) -> Web3:
        """
        Backward-compatible access to the underlying Web3 instance.
        """
        return self.w3

    # ========================================================
    # CONNECTION
    # ========================================================

    def is_connected(self) -> bool:
        """
        Return whether the Ethereum RPC connection is alive.
        """
        return self.w3.is_connected()

    # ========================================================
    # BLOCKS
    # ========================================================

    def latest_block(self) -> int:
        """
        Return the latest Ethereum block number.
        """
        return self.w3.eth.block_number

    def get_block(
        self,
        block_number: int,
        full_transactions: bool = True,
    ):
        """
        Retrieve an Ethereum block.
        """
        return self.w3.eth.get_block(
            block_number,
            full_transactions=full_transactions,
        )

    def get_block_transaction_hashes(
        self,
        block_number: int,
    ) -> list[Any]:
        """
        Retrieve only the transaction hashes from a block.

        This avoids downloading complete transaction objects
        when they are not required.
        """
        block = self.get_block(
            block_number,
            full_transactions=False,
        )

        return list(
            block["transactions"]
        )

    # ========================================================
    # TRANSACTIONS
    # ========================================================

    def get_transaction(
        self,
        tx_hash: str,
    ):
        """
        Retrieve a transaction by hash.
        """
        return self.w3.eth.get_transaction(
            tx_hash
        )

    def get_transaction_receipt(
        self,
        tx_hash: str,
    ):
        """
        Retrieve a transaction receipt by hash.
        """
        return self.w3.eth.get_transaction_receipt(
            tx_hash
        )

    # ========================================================
    # LOGS
    # ========================================================

    def get_logs(
        self,
        from_block: int,
        to_block: int,
        address: str | list[str] | None = None,
        topics: list[Any] | None = None,
    ):
        """
        Retrieve Ethereum event logs over a block range.
        """

        if from_block < 0:
            raise ValueError(
                "from_block must be non-negative"
            )

        if to_block < from_block:
            raise ValueError(
                "to_block must be >= from_block"
            )

        filter_params: dict[str, Any] = {
            "fromBlock": from_block,
            "toBlock": to_block,
        }

        if address is not None:
            filter_params["address"] = address

        if topics is not None:
            filter_params["topics"] = topics

        return self.w3.eth.get_logs(
            filter_params
        )

    # ========================================================
    # RECEIPTS
    # ========================================================

    def get_block_receipts(
        self,
        block_number: int,
    ) -> list[Any]:
        """
        Retrieve all transaction receipts for a block.

        Uses the standard transaction-receipt RPC path so this
        works with providers that do not expose a dedicated
        eth_getBlockReceipts method.
        """

        transaction_hashes = (
            self.get_block_transaction_hashes(
                block_number
            )
        )

        receipts: list[Any] = []

        for tx_hash in transaction_hashes:
            receipts.append(
                self.get_transaction_receipt(
                    tx_hash
                )
            )

        return receipts

    def get_receipts(
        self,
        transaction_hashes: Iterable[Any],
    ) -> list[Any]:
        """
        Retrieve receipts for multiple transactions.

        This method provides a reusable batch-processing boundary
        for higher-level scanners.
        """

        receipts: list[Any] = []

        for tx_hash in transaction_hashes:
            receipts.append(
                self.get_transaction_receipt(
                    tx_hash
                )
            )

        return receipts

    # ========================================================
    # GAS
    # ========================================================

    def gas_price(self) -> int:
        """
        Return the current network gas price in wei.
        """
        return self.w3.eth.gas_price

    def get_transaction_count(
        self,
        address: str,
    ) -> int:
        """
        Return the transaction count / nonce for an address.
        """
        return self.w3.eth.get_transaction_count(
            Web3.to_checksum_address(
                address
            )
        )

    # ========================================================
    # CHAIN STATE
    # ========================================================

    def chain_id(self) -> int:
        """
        Return the connected Ethereum chain ID.
        """
        return self.w3.eth.chain_id

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    def health_check(self) -> dict[str, Any]:
        """
        Return basic RPC health information.

        Useful for monitoring and failure detection.
        """

        connected = self.is_connected()

        if not connected:
            return {
                "connected": False,
                "chain_id": None,
                "latest_block": None,
            }

        return {
            "connected": True,
            "chain_id": self.chain_id(),
            "latest_block": self.latest_block(),
        }