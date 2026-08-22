# On-Chain MEV Engine

A research-grade educational project for understanding and building an on-chain MEV engine from first principles.

The project progressively evolves from AMM mathematics into a real-time Ethereum MEV detection, opportunity analysis, execution simulation, and strategy evaluation pipeline.

The overall progression is:

    AMM Mathematics
          ↓
    Arbitrage Simulation
          ↓
    Ethereum RPC Connectivity
          ↓
    Real Uniswap State
          ↓
    Uniswap V3 Mathematics
          ↓
    Cross-Pool Arbitrage
          ↓
    MEV Detection
          ↓
    Production Block Processing
          ↓
    Real-Time MEV Pipeline
          ↓
    Opportunity Detection
          ↓
    Execution Simulation
          ↓
    MEV Strategy Layer
          ↓
    Backtesting & Evaluation


---

# Project Goal

The goal of this project is to understand how a real MEV system can be constructed layer by layer.

Instead of starting with a black-box trading bot, the project separates:

    Blockchain Data
          ↓
    Protocol Events
          ↓
    Market State
          ↓
    Opportunity Detection
          ↓
    Strategy Selection
          ↓
    Execution Simulation
          ↓
    Profitability Analysis

Every major layer is independently testable.


---

# System Architecture

The current architecture can be summarized as:

    ┌───────────────────────────────┐
    │        Ethereum RPC          │
    │                               │
    │ Blocks / Transactions / Logs  │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │       Blockchain Client        │
    │                               │
    │ RPC abstraction               │
    │ Block retrieval               │
    │ Transaction receipts          │
    │ Event logs                    │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │        Swap Detection         │
    │                               │
    │ Uniswap V2 events             │
    │ Uniswap V3 events             │
    │ Pool metadata                 │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │        Market State           │
    │                               │
    │ Pool prices                   │
    │ Liquidity                     │
    │ Swap observations             │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │    Opportunity Detection      │
    │                               │
    │ Cross-pool price differences  │
    │ Spread calculation            │
    │ Gross profit estimation       │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │      Strategy Layer           │
    │                               │
    │ Arbitrage                     │
    │ Sandwich simulation           │
    │ Strategy selection            │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │     Execution Simulator       │
    │                               │
    │ Gas costs                     │
    │ Slippage                      │
    │ Net profitability             │
    │ Local state simulation        │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │      Evaluation Layer         │
    │                               │
    │ Backtesting                   │
    │ Strategy statistics           │
    │ Profitability analysis        │
    └───────────────────────────────┘


---

# Milestone Progress

## Milestone 1 — AMM & Arbitrage

Built a constant-product AMM from first principles.

Implemented:

- AMM reserves
- Constant-product invariant
- Spot price
- Trading fees
- Swap calculations
- Pool state updates
- Arbitrage simulation
- Arbitrage PnL
- Trade-size optimization
- Unit tests

Core model:

    x * y = k


---

## Milestone 2 — Ethereum Connectivity

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
- Gas price retrieval
- Transaction count retrieval


---

## Milestone 3 — Real Uniswap State

Connected the engine directly to real Uniswap contracts on Ethereum.

### Uniswap V2

Implemented:

- Factory lookup
- Pair discovery
- Token identification
- Real reserves
- Spot price calculation
- Swap simulation
- Real pool state

### Uniswap V3

Connected to the WETH/USDC 0.05% pool:

    0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640

Implemented retrieval of:

- slot0
- sqrtPriceX96
- Current tick
- Active liquidity
- Pool fee
- Tick spacing
- Tick bitmap
- Tick information


---

# Uniswap V3 Architecture

Unlike V2, Uniswap V3 concentrates liquidity into specific price ranges.

The swap engine therefore needs to model:

    Current sqrt price
          ↓
    Active liquidity
          ↓
    Calculate swap step
          ↓
    Find next initialized tick
          ↓
    Cross tick
          ↓
    Update liquidity
          ↓
    Continue
          ↓
    Final amountOut


This project implements the mathematical foundation required for this process.


---

## Milestone 4 — Uniswap V3 Swap Engine

Implemented:

- Q96 fixed-point mathematics
- sqrt-price calculations
- Amount0 calculations
- Amount1 calculations
- Swap step calculations
- Tick traversal
- Tick bitmap handling
- Tick crossing
- Liquidity updates
- Multi-step swaps
- V3 swap tests

The V3 implementation now models the concentrated-liquidity mechanics instead of treating the pool as a simple V2-style constant-product AMM.


---

## Milestone 5 — Cross-Pool Arbitrage

Implemented cross-pool arbitrage between real Uniswap pools.

Implemented:

- V2 → V3 arbitrage
- V3 → V2 arbitrage
- Trade-size simulation
- Trade-size optimization
- Slippage
- Gas costs
- Gross profit
- Net profit
- Profitability checks

The system can compare different pool states and determine whether an arbitrage route is economically viable.


---

## Milestone 6 — MEV Detection

Built the first event-driven MEV detection layer.

Implemented:

- Ethereum block analysis
- Transaction receipt processing
- Uniswap V2 Swap event detection
- Uniswap V3 Swap event detection
- DEX identification
- Pool metadata
- Event normalization
- Swap classification
- Transaction ordering
- Log ordering

The system converts raw Ethereum logs into normalized swap events.


---

## Milestone 7 — MEV Simulation

Extended the engine from event detection into MEV simulation.

Implemented:

- Transaction ordering
- Multi-transaction state modelling
- Price impact analysis
- Arbitrage modelling
- Sandwich modelling
- Gas-aware profitability
- Execution feasibility analysis

The objective is to model what could happen if transactions were executed in a particular order.


---

## Milestone 8 — Production Architecture

Introduced a production-oriented processing architecture.

Implemented:

- Block streaming
- Async processing
- Persistent market state
- Opportunity queues
- Metrics
- Latency measurement
- Failure handling
- Block validation
- State replacement
- Multi-block processing

The engine moved from isolated scripts toward a continuously running pipeline.


---

## Milestone 9 — Real-Time Blockchain Pipeline

Connected the production architecture to real Ethereum blocks.

Implemented:

- Real-time block processing
- Ethereum block stream
- Swap discovery
- Market observations
- Opportunity detection
- Pipeline metrics
- Continuous processing architecture

The real-time pipeline is:

    Ethereum Blocks
          ↓
    Block Stream
          ↓
    Swap Detection
          ↓
    Market Observations
          ↓
    Opportunity Detection
          ↓
    MEV Opportunities


---

## Milestone 10 — MEV Opportunity Detection

Implemented a dedicated opportunity detection layer.

The system now separates:

    Raw Swap Events
          ↓
    Market Observations
          ↓
    Price Comparison
          ↓
    Arbitrage Opportunity
          ↓
    Profitability Estimate

Implemented:

- Pool observation model
- Cross-pool price comparison
- Spread calculation
- Spread percentage
- Gross profit estimation
- Minimum-spread filtering
- Opportunity ranking
- Real-time opportunity detection

Example:

    V2 Price
       │
       │
       ├───────────────┐
       │               │
       ▼               ▼
    Buy Pool        Sell Pool
       │               │
       └───────┬───────┘
               │
               ▼
        Price Difference
               │
               ▼
         MEV Opportunity


---

## Milestone 11 — Execution Simulation & MEV Strategy Layer

Added a dedicated execution and strategy layer on top of opportunity detection.

The architecture became:

    Opportunity
         ↓
    Strategy Selection
         ↓
    Execution Simulation
         ↓
    Gas Estimation
         ↓
    Gross Profit
         ↓
    Net Profit
         ↓
    Profitability Decision


Implemented:

- Execution simulator
- Gas cost calculation
- Native-token price modelling
- Arbitrage strategy simulation
- Sandwich strategy simulation
- Net profit calculation
- Profitability evaluation
- Local pool-state simulation
- Strategy abstraction
- Strategy result models

Example execution result:

    Gross Profit
         ↓
      - Gas
         ↓
    Net Profit
         ↓
    Profitable?
       /   \
     Yes    No


The simulator deliberately does not sign or broadcast transactions.

All execution is performed against copied local state.


---

# Final Milestone — Backtesting & Strategy Evaluation

The final stage of the project focuses on evaluating the strategies built throughout the previous milestones.

The objective is no longer simply:

    "Can the engine detect an opportunity?"

Instead:

    "How would the strategy have performed across historical opportunities?"


The final evaluation layer can analyze:

- Historical blocks
- Historical swaps
- Historical price differences
- Historical opportunities
- Strategy profitability
- Gas-adjusted returns
- Number of opportunities
- Win rate
- Average profit
- Maximum profit
- Maximum loss
- Strategy performance


The conceptual architecture becomes:

    Historical Ethereum Blocks
              ↓
       Historical Swaps
              ↓
        Market State
              ↓
      Opportunity Detection
              ↓
       Strategy Simulation
              ↓
        Execution Model
              ↓
       Profitability Model
              ↓
          Statistics
              ↓
        Strategy Evaluation


---

# Project Structure

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
    │   ├── cross_pool_arbitrage.py
    │   ├── production_engine.py
    │   ├── realtime_engine.py
    │   ├── opportunity_engine.py
    │   └── mev_strategy_engine.py
    │
    ├── src/
    │   │
    │   ├── amm/
    │   │   ├── pool.py
    │   │   ├── math.py
    │   │   ├── arbitrage.py
    │   │   ├── optimizer.py
    │   │   └── simulator.py
    │   │
    │   ├── blockchain/
    │   │   ├── client.py
    │   │   ├── events.py
    │   │   ├── swap_detection.py
    │   │   ├── uniswap_v2.py
    │   │   └── uniswap_v3.py
    │   │
    │   └── mev/
    │       ├── block_scanner.py
    │       ├── block_stream.py
    │       ├── opportunity.py
    │       ├── execution.py
    │       └── strategy.py
    │
    ├── tests/
    │   ├── test_pool.py
    │   ├── test_arbitrage.py
    │   ├── test_block_scanner.py
    │   ├── test_block_stream.py
    │   ├── test_mev_detection.py
    │   ├── test_opportunity.py
    │   ├── test_production.py
    │   ├── test_execution.py
    │   ├── test_strategy.py
    │   ├── test_slippage.py
    │   │
    │   └── test_v3/
    │       ├── test_math.py
    │       ├── test_pool.py
    │       ├── test_swap.py
    │       └── test_tick_state.py
    │
    ├── pyproject.toml
    ├── .env
    └── README.md


---

# Testing

Run the complete test suite:

    python -m pytest -vv

The test suite covers the major components of the engine.

Coverage includes:

- AMM mathematics
- Pool behaviour
- Swap calculations
- Arbitrage
- Trade optimization
- Slippage
- Ethereum connectivity abstractions
- V2 event decoding
- V3 event decoding
- V3 swap mathematics
- Tick traversal
- Tick bitmap handling
- Block scanning
- Block streaming
- Market-state persistence
- Production metrics
- Opportunity detection
- Execution simulation
- MEV strategy evaluation


---

# Example Commands

## Run AMM experiments

    python -m research.amm_experiments


## Run arbitrage experiments

    python -m research.arbitrage_experiment


## Inspect Ethereum

    python -m research.ethereum_experiment


## Inspect transactions

    python -m research.transaction_experiment


## Inspect Uniswap V2

    python -m research.uniswap_experiment


## Inspect real AMM state

    python -m research.real_amm_experiment


## Inspect Uniswap V3

    python -m research.uniswap_v3_experiment


## Inspect V3 state

    python -m research.v3_state


## Run cross-pool arbitrage

    python -m research.cross_pool_arbitrage


## Run production architecture

    python -m research.production_engine


## Run real-time pipeline

    python -m research.realtime_engine


## Run opportunity detection

    python -m research.opportunity_engine


## Run execution and strategy simulation

    python -m research.mev_strategy_engine


---

# Core Concepts

## AMM

An Automated Market Maker is a protocol where prices are determined algorithmically from liquidity rather than through a traditional order book.


## Constant Product

Uniswap V2 uses:

    x * y = k


## Concentrated Liquidity

Uniswap V3 allows liquidity providers to choose the price range where their liquidity is active.


## Tick

A discrete price boundary in Uniswap V3.

Crossing a tick can change the active liquidity available to a swap.


## MEV

Maximal Extractable Value.

MEV represents value that can potentially be extracted from transaction ordering and execution within a blockchain block.


## Arbitrage

Arbitrage attempts to exploit price differences for the same asset across different markets.

Conceptually:

    Buy Cheap
        ↓
    Sell Expensive
        ↓
    Gross Profit
        ↓
    - Costs
        ↓
    Net Profit


## Sandwich

A sandwich strategy models transactions placed before and after a victim transaction.

Conceptually:

    Attacker Buy
          ↓
    Victim Swap
          ↓
    Attacker Sell
          ↓
    Profit / Loss


## Slippage

Slippage represents the difference between the expected execution price and the actual execution price.

Large trades generally cause larger price impact in AMMs.


## Gas

Ethereum execution requires gas.

Therefore a theoretical arbitrage opportunity is not necessarily profitable.

The actual decision should consider:

    Net Profit =
        Gross Profit
        - Gas Cost
        - Other Execution Costs


---

# Design Philosophy

The project follows a progression from mathematical models to blockchain infrastructure and strategy evaluation.

The core philosophy is:

    Understand
        ↓
    Implement
        ↓
    Test
        ↓
    Connect to Reality
        ↓
    Measure
        ↓
    Simulate
        ↓
    Evaluate


Each layer has a clear responsibility.

### Blockchain Layer

Responsible for obtaining Ethereum data.

### Protocol Layer

Responsible for decoding Uniswap events and understanding pool mechanics.

### Market Layer

Responsible for maintaining normalized market observations.

### Opportunity Layer

Responsible for identifying potentially profitable market differences.

### Strategy Layer

Responsible for deciding how an opportunity could theoretically be exploited.

### Execution Layer

Responsible for modelling gas, slippage, and profitability.

### Evaluation Layer

Responsible for measuring strategy performance.


---

# Important Architectural Principle

The project deliberately separates:

    Detection
        ≠
    Decision
        ≠
    Execution


Detection answers:

    "Is there a potentially interesting market event?"


Decision answers:

    "Is there a strategy worth considering?"


Execution simulation answers:

    "Would the strategy actually be profitable after costs?"


This separation makes the system easier to test and extend.


---

# Current Capabilities

The engine can now:

- Connect to Ethereum
- Inspect real blocks
- Inspect transaction receipts
- Decode Uniswap V2 swaps
- Decode Uniswap V3 swaps
- Maintain normalized swap observations
- Model Uniswap V2 liquidity
- Model Uniswap V3 concentrated liquidity
- Simulate V3 swaps
- Compare multiple pools
- Detect cross-pool price differences
- Detect potential arbitrage opportunities
- Simulate MEV strategies
- Model gas costs
- Calculate gross profit
- Calculate net profit
- Determine theoretical profitability
- Process blocks in a production-style pipeline
- Process real-time Ethereum data
- Maintain persistent market state
- Measure pipeline latency
- Handle processing failures


---

# What This Project Does NOT Do

This project intentionally does not:

- Sign real transactions
- Store private keys
- Broadcast transactions
- Execute trades on mainnet
- Control transaction ordering
- Operate a production trading bot
- Guarantee profitability
- Guarantee execution

The execution layer is a simulation and research environment.


---

# Configuration

The Ethereum RPC endpoint is loaded from the environment.

Create a `.env` file:

    ETH_RPC_URL=YOUR_ETHEREUM_RPC_URL


The project expects a working Ethereum RPC provider.

Do not commit private credentials or API keys to GitHub.


---

# Research Direction

Although the core implementation is complete as an educational MEV engine, several areas could be explored further.

Possible extensions include:

- Historical backtesting
- More DEX integrations
- Uniswap V3 multi-pool routing
- Curve integration
- Balancer integration
- Flash-loan modelling
- More sophisticated gas estimation
- Priority-fee modelling
- Builder/relay simulation
- Transaction bundle simulation
- Reorg handling
- Mempool monitoring
- Historical opportunity databases
- Statistical strategy evaluation
- Machine-learning-based opportunity ranking


---

# Final Architecture

The complete project can be viewed as:

    ┌─────────────────────────────────────────┐
    │              Ethereum                   │
    │                                         │
    │ Blocks / Transactions / Logs / State    │
    └────────────────────┬────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────┐
    │          Blockchain Client              │
    └────────────────────┬────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────┐
    │          Block Stream / Scanner          │
    └────────────────────┬────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────┐
    │            Swap Detection               │
    │                                         │
    │        V2 Events / V3 Events            │
    └────────────────────┬────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────┐
    │            Market State                 │
    │                                         │
    │ Pools / Prices / Liquidity / Swaps      │
    └────────────────────┬────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────┐
    │        Opportunity Detection            │
    │                                         │
    │     Spread / Arbitrage / Candidates     │
    └────────────────────┬────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────┐
    │            Strategy Layer               │
    │                                         │
    │ Arbitrage / Sandwich / Other Strategies │
    └────────────────────┬────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────┐
    │         Execution Simulation            │
    │                                         │
    │ Slippage / Gas / Gross / Net Profit     │
    └────────────────────┬────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────┐
    │         Strategy Evaluation             │
    │                                         │
    │ Backtesting / Statistics / Performance  │
    └─────────────────────────────────────────┘


---

# Lessons From the Project

The project demonstrates several important ideas behind real MEV infrastructure:

1. Blockchain data must first be normalized before it can be analyzed.

2. Detecting a swap does not mean an MEV opportunity exists.

3. Detecting a price difference does not mean the trade is profitable.

4. Gas costs can eliminate apparently profitable opportunities.

5. Slippage and liquidity matter when estimating execution.

6. Strategy logic should remain separate from blockchain infrastructure.

7. Execution should be simulated before any real transaction is considered.

8. Testing every layer independently makes complex systems easier to reason about.

9. Real-time systems require state management, failure handling, and latency measurement in addition to financial logic.

10. A complete MEV engine is not simply an arbitrage formula; it is a pipeline connecting blockchain data, market state, opportunity detection, strategy selection, and execution modelling.


---

# Final Status

This repository represents a complete educational MEV research pipeline built progressively from first principles.

The project evolved through:

    AMM Mathematics
          ↓
    Arbitrage
          ↓
    Ethereum
          ↓
    Uniswap
          ↓
    V3 Mathematics
          ↓
    Cross-Pool Arbitrage
          ↓
    MEV Detection
          ↓
    Production Processing
          ↓
    Real-Time Processing
          ↓
    Opportunity Detection
          ↓
    Strategy Simulation
          ↓
    Execution Modelling
          ↓
    Strategy Evaluation


---

# Disclaimer

This is an educational and research project.

It is not intended to execute trades or interact with mainnet funds.

No private keys are required by the project, and the execution layer is designed for local simulation rather than real transaction broadcasting.