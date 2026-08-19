# On-Chain MEV Engine

A research project for understanding and building an on-chain MEV engine from first principles.

The project starts with AMM mathematics and gradually connects the simulator to real Ethereum and Uniswap state.

The goal is to move from:

    AMM mathematics
          ↓
    Arbitrage simulation
          ↓
    Real Ethereum data
          ↓
    Real Uniswap state
          ↓
    V3 concentrated liquidity
          ↓
    Cross-pool arbitrage
          ↓
    MEV opportunity detection

---

## Current Progress

### Milestone 1 — AMM & Arbitrage

Built a constant-product AMM using:

    x * y = k

Implemented:

- AMM reserves
- Spot price
- Trading fees
- Swap calculations
- Pool state updates
- Arbitrage simulation
- Arbitrage PnL
- Trade-size optimization
- Unit tests

The engine can simulate arbitrage between two AMMs and determine whether a trade is profitable.

---

### Milestone 2 — Ethereum Connectivity

Connected the engine to a real Ethereum RPC.

Implemented:

- Ethereum RPC client
- Latest block retrieval
- Block inspection
- Transaction retrieval
- Transaction receipts
- Event logs
- ERC-20 Transfer decoding
- Token decimal conversion

The engine can now inspect real Ethereum transactions instead of relying only on simulated data.

---

### Milestone 3 — Real Uniswap State

Connected directly to Uniswap contracts on Ethereum.

Implemented:

### Uniswap V2

- Factory lookup
- Pair discovery
- Token identification
- Real reserves
- Spot price calculation
- Real pool state
- Swap simulation using real reserves

### Uniswap V3

Connected to the WETH/USDC 0.05% pool:

    0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640

Implemented retrieval of:

- `slot0`
- `sqrtPriceX96`
- Current tick
- Active liquidity
- Pool fee
- Tick spacing
- Tick bitmap
- Tick information

Example live state:

    fee:          500
    tick spacing: 10
    liquidity:    18080787383309250914

---

## V3 Architecture

Unlike V2, Uniswap V3 does not use one constant-product curve across the entire price range.

Liquidity is concentrated into individual price ranges.

The swap engine therefore needs to:

    Current price
          ↓
    Active liquidity
          ↓
    Calculate next price
          ↓
    Find next initialized tick
          ↓
    Cross tick if required
          ↓
    Update liquidity
          ↓
    Continue swap
          ↓
    Final amountOut

This is the next major component of the project.

---

## Project Structure

    onchain-mev-engine/
    │
    ├── docs/
    │   └── amm.md
    │
    ├── research/
    │   ├── amm_experiments.py
    │   ├── arbitrage_experiment.py
    │   ├── ethereum_experiment.py
    │   ├── transaction_experiment.py
    │   ├── uniswap_experiment.py
    │   ├── real_amm_experiment.py
    │   ├── uniswap_v3_experiment.py
    │   ├── v3_state.py
    │   └── cross_pool_arbitrage.py
    │
    ├── src/
    │   ├── amm/
    │   │   ├── pool.py
    │   │   ├── math.py
    │   │   ├── arbitrage.py
    │   │   ├── optimizer.py
    │   │   └── simulator.py
    │   │
    │   └── blockchain/
    │       ├── client.py
    │       ├── uniswap_v2.py
    │       └── uniswap_v3.py
    │
    ├── tests/
    │   ├── test_pool.py
    │   ├── test_arbitrage.py
    │   └── test_v3/
    │       ├── test_math.py
    │       └── test_swap.py
    │
    ├── pyproject.toml
    └── README.md

---

## Testing

Run the complete test suite:

    python -m pytest

Current test suite:

    16 passed

Tests cover:

- AMM calculations
- Swap behaviour
- Arbitrage
- Optimization
- V3 mathematical primitives
- V3 swap calculations

---

## Design Philosophy

The project intentionally follows a progression from simplified models to real blockchain infrastructure.

Instead of starting with a black-box MEV bot, each layer is implemented and validated independently:

    Mathematics
        ↓
    Simulation
        ↓
    Testing
        ↓
    Blockchain connectivity
        ↓
    Real protocol state
        ↓
    Execution model

This makes it easier to understand where an MEV opportunity actually comes from.

---

## Roadmap

### Milestone 4 — Real Uniswap V3 Swap Engine

- V3 sqrt-price mathematics
- Amount0 / amount1 calculations
- Tick traversal
- Tick bitmap scanning
- Liquidity updates
- Multi-tick swaps
- Exact V3 amountOut
- V3 swap tests

### Milestone 5 — Cross-Pool Arbitrage

- Real V2 → V3 simulation
- Real V3 → V2 simulation
- Optimal trade sizing
- Slippage
- Gas costs
- Net profitability

### Milestone 6 — MEV Detection

- Block transaction analysis
- Swap detection
- DEX identification
- Price impact detection
- Arbitrage opportunity detection
- Candidate transaction ranking

### Milestone 7 — MEV Simulation

- Transaction ordering
- Front-run / back-run modelling
- Sandwich detection
- Multi-transaction state simulation
- Gas-aware profitability

### Milestone 8 — Production Architecture

- Streaming blockchain data
- Async processing
- Persistent market state
- Opportunity queue
- Latency measurement
- Monitoring
- Failure handling

---

## Important Concepts

### AMM

Automated Market Maker.

A protocol where prices are determined algorithmically from liquidity rather than through a traditional order book.

### Constant Product

Uniswap V2 uses:

    x * y = k

### Concentrated Liquidity

Uniswap V3 allows liquidity providers to choose the price range where their liquidity is active.

### Tick

A discrete price boundary in Uniswap V3.

Crossing a tick can change the active liquidity available to the swap.

### MEV

Maximal Extractable Value.

The value that can potentially be extracted by controlling or influencing transaction ordering within a block.

### Arbitrage

Buying an asset where it is cheaper and selling it where it is more expensive.

---

## Disclaimer

This is an educational and research project.

It is not intended to execute trades or interact with mainnet funds.