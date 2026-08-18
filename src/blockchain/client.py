import os

from dotenv import load_dotenv
from web3 import Web3


load_dotenv()


class EthereumClient:

    def __init__(self):

        rpc_url = os.getenv("ETH_RPC_URL")

        if not rpc_url:
            raise ValueError(
                "ETH_RPC_URL is not set. "
                "Add it to the .env file."
            )

        self.w3 = Web3(
            Web3.HTTPProvider(rpc_url)
        )

        if not self.w3.is_connected():
            raise ConnectionError(
                "Could not connect to Ethereum RPC. "
                "Check ETH_RPC_URL."
            )

    def latest_block(self) -> int:
        return self.w3.eth.block_number
    
    def get_block(self, block_number: int):
        return self.w3.eth.get_block(
            block_number,
            full_transactions=True,
        )

    def get_transaction(self, tx_hash: str):
        return self.w3.eth.get_transaction(tx_hash)

    def get_transaction_receipt(self, tx_hash: str):
        return self.w3.eth.get_transaction_receipt(tx_hash)

    def get_logs(self, from_block: int, to_block: int):
        return self.w3.eth.get_logs({
            "fromBlock": from_block,
            "toBlock": to_block,
        })  