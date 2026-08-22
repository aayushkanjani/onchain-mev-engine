from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from web3 import Web3


load_dotenv()


class EthereumClient:
    """
    Thin Ethereum RPC wrapper.

    The client is deliberately kept separate from MEV logic.

    Blockchain layer:
        RPC → raw Ethereum data

    MEV layer:
        raw data → decoded events → opportunities
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

    # ========================================================
    # BLOCKS
    # ========================================================

    def latest_block(self) -> int:
        return self.w3.eth.block_number

    def get_block(
        self,
        block_number: int,
        full_transactions: bool = True,
    ):
        return self.w3.eth.get_block(
            block_number,
            full_transactions=full_transactions,
        )

    # ========================================================
    # TRANSACTIONS
    # ========================================================

    def get_transaction(
        self,
        tx_hash: str,
    ):
        return self.w3.eth.get_transaction(
            tx_hash
        )

    def get_transaction_receipt(
        self,
        tx_hash: str,
    ):
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
    # TRANSACTION RECEIPT HELPERS
    # ========================================================

    def get_block_receipts(
        self,
        block_number: int,
    ) -> list[Any]:

        block = self.get_block(
            block_number,
            full_transactions=True,
        )

        receipts: list[Any] = []

        for tx in block["transactions"]:

            tx_hash = tx["hash"]

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
        return self.w3.eth.gas_price

    def get_transaction_count(
        self,
        address: str,
    ) -> int:

        return self.w3.eth.get_transaction_count(
            Web3.to_checksum_address(
                address
            )
        )