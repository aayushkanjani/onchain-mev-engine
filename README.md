# On-Chain MEV Engine

A research-oriented MEV and DeFi trading system built from scratch.

The goal is to understand how real on-chain trading infrastructure works — from
reading Ethereum state and decoding transactions to AMM pricing, arbitrage,
MEV detection, and eventually transaction-level execution analysis.

This project is intentionally built incrementally, starting with the underlying
mathematics and gradually connecting it to real Ethereum data.

---

## Current Progress

### Milestone 1 — AMM & Arbitrage Engine

Built a constant-product AMM based on:

    x * y = k

Implemented:

- Constant-product pricing
- AMM trading fees
- Swap simulation
- Spot price calculation
- Price impact
- Arbitrage simulation
- Arbitrage profit calculation
- Trade-size experiments
- Unit tests

---

### Milestone 2 — Ethereum Connectivity

Connected the system to Ethereum through an RPC endpoint.

Implemented:

- Ethereum RPC client
- Latest block retrieval
- Block metadata
- Transaction retrieval
- Transaction receipts
- Event logs

---

### Milestone 3 — On-Chain Transaction Decoding

Built transaction-level inspection and ERC-20 event decoding.

Implemented:

- Transaction inspection
- Receipt inspection
- Log parsing
- ERC-20 `Transfer` event decoding
- Raw token amount decoding
- Token decimal normalization

Example:

    Raw amount: 149265000
    USDC amount: 149.265

---

### Milestone 4 — Real Uniswap V2 State

Connected the AMM engine to a real Uniswap V2 pool.

The system now:

    Ethereum
        ↓
    Uniswap V2 Factory
        ↓
    WETH/USDC Pair
        ↓
    getReserves()
        ↓
    Real reserves
        ↓
    AMMPool
        ↓
    Swap simulation

Current pool:

    WETH/USDC
    Uniswap V2

Real on-chain state is converted from raw token units into human-readable
amounts and passed directly into the AMM engine.

Example simulation:

    USDC in:          $1,000.00
    WETH out:         0.52100883
    Spot price:       ~$1,913.38
    Effective price:  ~$1,919.35
    Trading fee:      $3.00

This demonstrates the difference between:

    Spot price
          ≠
    Execution price

because AMM trades experience fees and price impact.

---

## Architecture

    ┌─────────────────────────────────────┐
    │            Ethereum                 │
    │                                     │
    │   Blocks / Transactions / Logs      │
    └──────────────────┬──────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────┐
    │       Blockchain Data Layer         │
    │                                     │
    │  RPC Client                         │
    │  Transaction Decoder                │
    │  Uniswap V2 Adapter                 │
    └──────────────────┬──────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────┐
    │             AMM Engine              │
    │                                     │
    │  Constant Product                   │
    │  Fees                               │
    │  Price Impact                       │
    │  Swap Simulation                    │
    └──────────────────┬──────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────┐
    │         Arbitrage Engine            │
    │                                     │
    │  Cross-pool pricing                 │
    │  Trade sizing                       │
    │  Profit estimation                  │
    └──────────────────┬──────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────┐
    │            MEV Layer                │
    │                                     │
    │  Opportunity Detection              │
    │  Gas Estimation                     │
    │  Transaction Ordering               │
    │  MEV Analysis                       │
    └─────────────────────────────────────┘

---

## Project Structure

    onchain-mev-engine/
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
    │       └── uniswap_v2.py
    │
    ├── research/
    │   ├── amm_experiments.py
    │   ├── arbitrage_experiment.py
    │   ├── ethereum_experiment.py
    │   ├── transaction_experiment.py
    │   ├── uniswap_experiment.py
    │   └── real_amm_experiment.py
    │
    ├── tests/
    │   ├── test_pool.py
    │   └── test_arbitrage.py
    │
    ├── docs/
    │   └── amm.md
    │
    ├── pyproject.toml
    └── README.md

---

## Running the Project

Run the AMM experiments:

    python -m research.amm_experiments

Run arbitrage experiments:

    python -m research.arbitrage_experiment

Inspect Ethereum:

    python -m research.ethereum_experiment

Inspect and decode a transaction:

    python -m research.transaction_experiment

Query a real Uniswap V2 pool:

    python -m research.uniswap_experiment

Connect real Uniswap reserves to the AMM engine:

    python -m research.real_amm_experiment

Run tests:

    python -m pytest

---

## Design Philosophy

The project follows a simple principle:

    Understand the mathematics
            ↓
    Build the simulation
            ↓
    Connect to real blockchain state
            ↓
    Validate against real data
            ↓
    Build trading strategies
            ↓
    Study MEV

The core AMM logic is kept independent from the blockchain layer so that the
same pricing engine can operate on both simulated and real pool state.

---

## Roadmap

### Milestone 5 — Cross-DEX Arbitrage

- Query multiple real liquidity pools
- Compare prices
- Simulate both arbitrage legs
- Account for AMM fees
- Estimate gas costs
- Calculate net PnL
- Optimize trade size

### Milestone 6 — Uniswap V3

- Concentrated liquidity
- Ticks
- Tick spacing
- `sqrtPriceX96`
- Liquidity ranges
- V3 swap mathematics

### Milestone 7 — MEV Detection

- Pending transactions
- Large swaps
- Sandwich opportunities
- Backrunning
- Transaction ordering
- Gas bidding

### Milestone 8 — Historical MEV Research

- Historical blocks
- Swap reconstruction
- Arbitrage detection
- MEV opportunity classification
- Profit estimation
- Dataset generation

### Milestone 9 — Research / Production Architecture

- Async blockchain ingestion
- Concurrent RPC requests
- Caching
- Persistent market-state storage
- Opportunity pipeline
- Monitoring
- Backtesting

---

## Disclaimer

This project is for educational and research purposes.

It does not execute live trades or transactions.