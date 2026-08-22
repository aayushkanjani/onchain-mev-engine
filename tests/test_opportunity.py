from __future__ import annotations

from src.blockchain.swap_detection import PoolMetadata
from src.mev.opportunity import (
    MarketObservation,
    OpportunityDetector,
)


TOKEN0 = (
    "0x0000000000000000000000000000000000000001"
)

TOKEN1 = (
    "0x0000000000000000000000000000000000000002"
)

POOL_A = (
    "0x0000000000000000000000000000000000000010"
)

POOL_B = (
    "0x0000000000000000000000000000000000000020"
)


def make_pool_a() -> PoolMetadata:

    return PoolMetadata(
        address=POOL_A,
        dex="Uniswap",
        version="V2",
        token0=TOKEN0,
        token1=TOKEN1,
    )


def make_pool_b() -> PoolMetadata:

    return PoolMetadata(
        address=POOL_B,
        dex="Uniswap",
        version="V3",
        token0=TOKEN0,
        token1=TOKEN1,
        fee=500,
        tick_spacing=10,
    )


def test_observation_creation():

    detector = OpportunityDetector()

    observation = detector.observation_from_price(
        pool=make_pool_a(),
        price_token1_per_token0=100.0,
    )

    assert isinstance(
        observation,
        MarketObservation,
    )

    assert (
        observation.price_token1_per_token0
        == 100.0
    )

    assert (
        observation.price_token0_per_token1
        == 0.01
    )


def test_group_by_pair():

    detector = OpportunityDetector()

    first = detector.observation_from_price(
        pool=make_pool_a(),
        price_token1_per_token0=100.0,
    )

    second = detector.observation_from_price(
        pool=make_pool_b(),
        price_token1_per_token0=101.0,
    )

    grouped = detector.group_by_pair(
        [
            first,
            second,
        ]
    )

    assert len(grouped) == 1

    pair = next(
        iter(grouped.values())
    )

    assert len(pair) == 2


def test_detects_arbitrage():

    detector = OpportunityDetector(
        min_spread_percent=0.1
    )

    cheap = detector.observation_from_price(
        pool=make_pool_a(),
        price_token1_per_token0=100.0,
        block_number=100,
    )

    expensive = detector.observation_from_price(
        pool=make_pool_b(),
        price_token1_per_token0=102.0,
        block_number=100,
    )

    opportunities = detector.detect(
        [
            cheap,
            expensive,
        ]
    )

    assert len(opportunities) == 1

    opportunity = opportunities[0]

    assert (
        opportunity.buy_pool
        == POOL_A
    )

    assert (
        opportunity.sell_pool
        == POOL_B
    )

    assert (
        opportunity.buy_price
        == 100.0
    )

    assert (
        opportunity.sell_price
        == 102.0
    )

    assert (
        opportunity.gross_spread
        == 2.0
    )

    assert (
        opportunity.gross_spread_percent
        == 2.0
    )


def test_ignores_small_spread():

    detector = OpportunityDetector(
        min_spread_percent=1.0
    )

    first = detector.observation_from_price(
        pool=make_pool_a(),
        price_token1_per_token0=100.0,
    )

    second = detector.observation_from_price(
        pool=make_pool_b(),
        price_token1_per_token0=100.5,
    )

    opportunities = detector.detect(
        [
            first,
            second,
        ]
    )

    assert opportunities == []


def test_detects_reverse_price_direction():

    detector = OpportunityDetector(
        min_spread_percent=0.1
    )

    first = detector.observation_from_price(
        pool=make_pool_a(),
        price_token1_per_token0=102.0,
    )

    second = detector.observation_from_price(
        pool=make_pool_b(),
        price_token1_per_token0=100.0,
    )

    opportunities = detector.detect(
        [
            first,
            second,
        ]
    )

    assert len(opportunities) == 1

    opportunity = opportunities[0]

    assert (
        opportunity.buy_pool
        == POOL_B
    )

    assert (
        opportunity.sell_pool
        == POOL_A
    )


def test_single_pool_has_no_opportunity():

    detector = OpportunityDetector()

    observation = detector.observation_from_price(
        pool=make_pool_a(),
        price_token1_per_token0=100.0,
    )

    opportunities = detector.detect(
        [observation]
    )

    assert opportunities == []


def test_different_pairs_are_not_compared():

    detector = OpportunityDetector(
        min_spread_percent=0.1
    )

    other_token = (
        "0x0000000000000000000000000000000000000099"
    )

    pool = PoolMetadata(
        address=POOL_B,
        dex="Uniswap",
        version="V3",
        token0=TOKEN0,
        token1=other_token,
        fee=500,
        tick_spacing=10,
    )

    first = detector.observation_from_price(
        pool=make_pool_a(),
        price_token1_per_token0=100.0,
    )

    second = detector.observation_from_price(
        pool=pool,
        price_token1_per_token0=200.0,
    )

    opportunities = detector.detect(
        [
            first,
            second,
        ]
    )

    assert opportunities == []


def test_invalid_price():

    detector = OpportunityDetector()

    try:
        detector.observation_from_price(
            pool=make_pool_a(),
            price_token1_per_token0=0,
        )

        assert False

    except ValueError:
        assert True


def test_invalid_threshold():

    try:
        OpportunityDetector(
            min_spread_percent=-1.0
        )

        assert False

    except ValueError:
        assert True


def test_opportunities_are_ranked():

    detector = OpportunityDetector(
        min_spread_percent=0.1
    )

    pool_c = PoolMetadata(
        address=(
            "0x0000000000000000000000000000000000000030"
        ),
        dex="Uniswap",
        version="V2",
        token0=TOKEN0,
        token1=TOKEN1,
    )

    first = detector.observation_from_price(
        pool=make_pool_a(),
        price_token1_per_token0=100.0,
    )

    second = detector.observation_from_price(
        pool=make_pool_b(),
        price_token1_per_token0=101.0,
    )

    third = detector.observation_from_price(
        pool=pool_c,
        price_token1_per_token0=105.0,
    )

    opportunities = detector.detect(
        [
            first,
            second,
            third,
        ]
    )

    assert len(opportunities) == 3

    assert (
        opportunities[0].gross_spread_percent
        >= opportunities[1].gross_spread_percent
    )

    assert (
        opportunities[1].gross_spread_percent
        >= opportunities[2].gross_spread_percent
    )