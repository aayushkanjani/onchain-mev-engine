from dataclasses import dataclass


@dataclass
class AMMPool:
    """
    Simplified constant-product AMM.

    Invariant:
        x * y = k

    token_x and token_y are the two assets in the pool.
    """

    token_x: str
    token_y: str
    reserve_x: float
    reserve_y: float
    fee_rate: float = 0.003  # 0.3%

    @property
    def k(self) -> float:
        """Current constant-product invariant."""
        return self.reserve_x * self.reserve_y

    @property
    def spot_price_x_in_y(self) -> float:
        """
        Price of 1 unit of token X in terms of token Y.

        Example:
            100 ETH
            300,000 USDC

        Spot price = 3,000 USDC / ETH
        """
        return self.reserve_y / self.reserve_x

    @property
    def spot_price_y_in_x(self) -> float:
        """Price of 1 unit of token Y in terms of token X."""
        return self.reserve_x / self.reserve_y

    def calculate_fee(self, amount_in: float) -> float:
        """Calculate the trading fee."""
        if amount_in <= 0:
            raise ValueError("amount_in must be positive")

        return amount_in * self.fee_rate

    def get_amount_out(
        self,
        amount_in: float,
        token_in: str,
    ) -> float:
        """
        Calculate how much token_out the trader receives.

        This method only calculates the result.
        It does NOT modify the pool.
        """

        if amount_in <= 0:
            raise ValueError("amount_in must be positive")

        # Identify which reserve is the input
        # and which reserve is the output.
        if token_in == self.token_x:
            reserve_in = self.reserve_x
            reserve_out = self.reserve_y

        elif token_in == self.token_y:
            reserve_in = self.reserve_y
            reserve_out = self.reserve_x

        else:
            raise ValueError(f"Unknown token: {token_in}")

        # -------------------------------
        # Step 1: Calculate trading fee
        # -------------------------------

        fee = self.calculate_fee(amount_in)

        # -------------------------------
        # Step 2: Amount actually used
        # by the pricing formula
        # -------------------------------

        amount_in_after_fee = amount_in - fee

        # -------------------------------
        # Step 3: Constant-product formula
        # -------------------------------

        amount_out = (
            reserve_out * amount_in_after_fee
            / (reserve_in + amount_in_after_fee)
        )

        return amount_out

    def swap(
        self,
        amount_in: float,
        token_in: str,
    ) -> float:
        """
        Execute a swap and update the pool reserves.

        Returns:
            amount of token_out received by the trader.
        """

        amount_out = self.get_amount_out(
            amount_in=amount_in,
            token_in=token_in,
        )

        # The full amount sent by the trader enters
        # the pool. The fee remains with the pool.
        if token_in == self.token_x:

            self.reserve_x += amount_in
            self.reserve_y -= amount_out

        elif token_in == self.token_y:

            self.reserve_y += amount_in
            self.reserve_x -= amount_out

        else:
            raise ValueError(f"Unknown token: {token_in}")

        return amount_out