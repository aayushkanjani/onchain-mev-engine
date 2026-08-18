from web3 import Web3


FACTORY_ABI = [
    {
        "name": "getPair",
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
        ],
        "outputs": [
            {"name": "pair", "type": "address"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]


PAIR_ABI = [
    {
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "inputs": [],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "token1",
        "outputs": [{"name": "", "type": "address"}],
        "inputs": [],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "getReserves",
        "outputs": [
            {"name": "_reserve0", "type": "uint112"},
            {"name": "_reserve1", "type": "uint112"},
            {"name": "_blockTimestampLast", "type": "uint32"},
        ],
        "inputs": [],
        "stateMutability": "view",
        "type": "function",
    },
]


FACTORY_ADDRESS = Web3.to_checksum_address(
    "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
)

WETH_ADDRESS = Web3.to_checksum_address(
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
)

USDC_ADDRESS = Web3.to_checksum_address(
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
)


class UniswapV2Factory:

    def __init__(self, w3: Web3):

        self.contract = w3.eth.contract(
            address=FACTORY_ADDRESS,
            abi=FACTORY_ABI,
        )

    def get_pair(self, token_a: str, token_b: str) -> str:

        return self.contract.functions.getPair(
            token_a,
            token_b,
        ).call()


class UniswapV2Pool:

    def __init__(self, w3: Web3, address: str):

        self.w3 = w3

        self.address = Web3.to_checksum_address(address)

        self.contract = w3.eth.contract(
            address=self.address,
            abi=PAIR_ABI,
        )

    def token0(self):
        return self.contract.functions.token0().call()

    def token1(self):
        return self.contract.functions.token1().call()

    def reserves(self):

        reserve0, reserve1, timestamp = (
            self.contract
            .functions
            .getReserves()
            .call()
        )

        return {
            "reserve0": reserve0,
            "reserve1": reserve1,
            "timestamp": timestamp,
        }