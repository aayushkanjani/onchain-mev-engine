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