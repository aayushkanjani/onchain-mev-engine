from src.amm.pool import AMMPool
from src.mev.execution_simulator import (
    ExecutionSimulator,
)
from src.mev.strategies import (
    StrategyEngine,
    StrategyType,
)


def make_buy_pool():
    return AMMPool(
        token_x="USDC",
        token_y="WETH",
        reserve_x=1_000_000.0,
        reserve_y=500.0,
        fee_rate=0.003,
    )


def make_sell_pool():
    return AMMPool(
        token_x="USDC",
        token_y="WETH",
        reserve_x=1_000_000.0,
        reserve_y=480.0,
        fee_rate=0.003,
    )


def test_simulator_gas_cost():

    simulator = ExecutionSimulator(
        gas_used=250_000,
        gas_price_gwei=20.0,
        native_token_price=2_500.0,
    )

    assert simulator.gas_cost_native == 0.005
    assert simulator.gas_cost_usd == 12.5


def test_arbitrage_simulation_does_not_mutate_pools():

    buy_pool = make_buy_pool()
    sell_pool = make_sell_pool()

    original_buy_x = buy_pool.reserve_x
    original_buy_y = buy_pool.reserve_y

    original_sell_x = sell_pool.reserve_x
    original_sell_y = sell_pool.reserve_y

    simulator = ExecutionSimulator(
        gas_used=1,
        gas_price_gwei=1,
        native_token_price=1,
    )

    result = simulator.simulate_arbitrage(
        buy_pool=buy_pool,
        sell_pool=sell_pool,
        amount_in=10_000.0,
        token_in="USDC",
    )

    assert len(result.trades) == 2

    assert buy_pool.reserve_x == original_buy_x
    assert buy_pool.reserve_y == original_buy_y

    assert sell_pool.reserve_x == original_sell_x
    assert sell_pool.reserve_y == original_sell_y


def test_arbitrage_has_two_legs():

    buy_pool = make_buy_pool()
    sell_pool = make_sell_pool()

    simulator = ExecutionSimulator(
        gas_used=1,
        gas_price_gwei=1,
        native_token_price=1,
    )

    result = simulator.simulate_arbitrage(
        buy_pool=buy_pool,
        sell_pool=sell_pool,
        amount_in=10_000.0,
        token_in="USDC",
    )

    assert result.trades[0].token_in == "USDC"
    assert result.trades[0].token_out == "WETH"

    assert result.trades[1].token_in == "WETH"
    assert result.trades[1].token_out == "USDC"


def test_sandwich_simulation_has_three_trades():

    pool = AMMPool(
        token_x="USDC",
        token_y="WETH",
        reserve_x=1_000_000.0,
        reserve_y=500.0,
        fee_rate=0.003,
    )

    simulator = ExecutionSimulator(
        gas_used=1,
        gas_price_gwei=1,
        native_token_price=1,
    )

    result = simulator.simulate_sandwich(
        pool=pool,
        victim_amount_in=10_000.0,
        victim_token_in="USDC",
        attacker_amount_in=1_000.0,
    )

    assert len(result.trades) == 3

    assert result.trades[0].token_in == "USDC"

    assert result.trades[1].token_in == "USDC"

    assert result.trades[2].token_in == "WETH"


def test_sandwich_does_not_mutate_pool():

    pool = AMMPool(
        token_x="USDC",
        token_y="WETH",
        reserve_x=1_000_000.0,
        reserve_y=500.0,
        fee_rate=0.003,
    )

    original_x = pool.reserve_x
    original_y = pool.reserve_y

    simulator = ExecutionSimulator(
        gas_used=1,
        gas_price_gwei=1,
        native_token_price=1,
    )

    simulator.simulate_sandwich(
        pool=pool,
        victim_amount_in=10_000.0,
        victim_token_in="USDC",
        attacker_amount_in=1_000.0,
    )

    assert pool.reserve_x == original_x
    assert pool.reserve_y == original_y


def test_strategy_engine_ranks_candidates():

    simulator = ExecutionSimulator(
        gas_used=1,
        gas_price_gwei=1,
        native_token_price=1,
    )

    engine = StrategyEngine(
        simulator
    )

    candidates = [
        type(
            "Candidate",
            (),
            {
                "net_profit": 10.0,
                "profitable": True,
            },
        )(),
        type(
            "Candidate",
            (),
            {
                "net_profit": 50.0,
                "profitable": True,
            },
        ),
        type(
            "Candidate",
            (),
            {
                "net_profit": 25.0,
                "profitable": True,
            },
        ),
    ]

    ranked = engine.rank(
        candidates
    )

    assert [
        candidate.net_profit
        for candidate in ranked
    ] == [
        50.0,
        25.0,
        10.0,
    ]


def test_profitable_only():

    simulator = ExecutionSimulator()

    engine = StrategyEngine(
        simulator
    )

    profitable = type(
        "Candidate",
        (),
        {
            "net_profit": 10.0,
            "profitable": True,
        },
    )()

    unprofitable = type(
        "Candidate",
        (),
        {
            "net_profit": -5.0,
            "profitable": False,
        },
    )()

    result = engine.profitable_only(
        [
            profitable,
            unprofitable,
        ]
    )

    assert result == [
        profitable
    ]