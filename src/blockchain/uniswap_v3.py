from web3 import Web3


FACTORY_ABI = [
    {
        "name": "getPool",
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
            {"name": "fee", "type": "uint24"},
        ],
        "outputs": [
            {"name": "pool", "type": "address"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]


POOL_ABI = [
    {
        "name": "slot0",
        "inputs": [],
        "outputs": [
            {"name": "sqrtPriceX96", "type": "uint160"},
            {"name": "tick", "type": "int24"},
            {"name": "observationIndex", "type": "uint16"},
            {"name": "observationCardinality", "type": "uint16"},
            {"name": "observationCardinalityNext", "type": "uint16"},
            {"name": "feeProtocol", "type": "uint8"},
            {"name": "unlocked", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "token0",
        "inputs": [],
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "token1",
        "inputs": [],
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "liquidity",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint128"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "fee",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint24"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "tickSpacing",
        "inputs": [],
        "outputs": [{"name": "", "type": "int24"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "tickBitmap",
        "inputs": [
            {"name": "wordPosition", "type": "int16"},
        ],
        "outputs": [
            {"name": "", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "name": "ticks",
        "inputs": [
            {"name": "tick", "type": "int24"},
        ],
        "outputs": [
            {"name": "liquidityGross", "type": "uint128"},
            {"name": "liquidityNet", "type": "int128"},
            {"name": "feeGrowthOutside0X128", "type": "uint256"},
            {"name": "feeGrowthOutside1X128", "type": "uint256"},
            {"name": "tickCumulativeOutside", "type": "int56"},
            {"name": "secondsPerLiquidityOutsideX128", "type": "uint160"},
            {"name": "secondsOutside", "type": "uint32"},
            {"name": "initialized", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


FACTORY_ADDRESS = Web3.to_checksum_address(
    "0x1F98431c8aD98523631AE4a59f267346ea31F984"
)


class UniswapV3Factory:

    def __init__(self, w3: Web3):
        self.contract = w3.eth.contract(
            address=FACTORY_ADDRESS,
            abi=FACTORY_ABI,
        )

    def get_pool(
        self,
        token_a: str,
        token_b: str,
        fee: int,
    ) -> str:

        return self.contract.functions.getPool(
            token_a,
            token_b,
            fee,
        ).call()


class UniswapV3Pool:

    def __init__(
        self,
        w3: Web3,
        address: str,
    ):

        self.address = Web3.to_checksum_address(address)

        self.contract = w3.eth.contract(
            address=self.address,
            abi=POOL_ABI,
        )

    def slot0(self):
        return self.contract.functions.slot0().call()

    def token0(self):
        return self.contract.functions.token0().call()

    def token1(self):
        return self.contract.functions.token1().call()

    def liquidity(self):
        return self.contract.functions.liquidity().call()

    def fee(self):
        return self.contract.functions.fee().call()

    def tick_spacing(self):
        return self.contract.functions.tickSpacing().call()

    def tick_bitmap(
        self,
        word_position: int,
    ) -> int:

        return self.contract.functions.tickBitmap(
            word_position
        ).call()

    def ticks(
        self,
        tick: int,
    ):

        return self.contract.functions.ticks(
            tick
        ).call()

    def get_tick_info(
        self,
        tick: int,
    ) -> dict:

        data = self.ticks(tick)

        return {
            "tick": tick,
            "liquidity_gross": data[0],
            "liquidity_net": data[1],
            "initialized": data[7],
        }