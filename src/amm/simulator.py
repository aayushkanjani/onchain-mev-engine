from pool import AMMPool


def main():

    # ----------------------------------------
    # Create our ETH / USDC liquidity pool
    # ----------------------------------------

    pool = AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100.0,
        reserve_y=300_000.0,
        fee_rate=0.003,
    )

    print("===================================")
    print("INITIAL POOL")
    print("===================================")

    print(f"ETH reserve:   {pool.reserve_x:.6f}")
    print(f"USDC reserve:  {pool.reserve_y:.6f}")
    print(f"Spot price:    ${pool.spot_price_x_in_y:.2f}")
    print(f"k:             {pool.k:.2f}")

    # ----------------------------------------
    # Trader wants to buy ETH using USDC
    # ----------------------------------------

    usdc_in = 3_000.0

    # ----------------------------------------
    # Calculate fee
    # ----------------------------------------

    fee = pool.calculate_fee(usdc_in)

    amount_after_fee = usdc_in - fee

    # ----------------------------------------
    # Calculate expected output
    # WITHOUT changing the pool
    # ----------------------------------------

    expected_eth = pool.get_amount_out(
        amount_in=usdc_in,
        token_in="USDC",
    )

    effective_price = usdc_in / expected_eth

    print("\n===================================")
    print("TRADE QUOTE")
    print("===================================")

    print(f"USDC sent:             ${usdc_in:.6f}")
    print(f"Trading fee:           ${fee:.6f}")
    print(f"Amount after fee:      ${amount_after_fee:.6f}")
    print(f"Expected ETH:          {expected_eth:.8f}")
    print(f"Effective price:       ${effective_price:.2f}")

    # ----------------------------------------
    # Execute the trade
    # ----------------------------------------

    eth_received = pool.swap(
        amount_in=usdc_in,
        token_in="USDC",
    )

    # ----------------------------------------
    # Pool after trade
    # ----------------------------------------

    print("\n===================================")
    print("AFTER SWAP")
    print("===================================")

    print(f"ETH received:          {eth_received:.8f}")
    print(f"ETH reserve:           {pool.reserve_x:.8f}")
    print(f"USDC reserve:          {pool.reserve_y:.8f}")
    print(f"New spot price:        ${pool.spot_price_x_in_y:.2f}")
    print(f"New k:                 {pool.k:.2f}")


if __name__ == "__main__":
    main()