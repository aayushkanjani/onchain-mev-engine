from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class MarketState:
    """
    Persistent market-state storage.

    SQLite is used as the first production-style persistence layer.

    Stored information:

        block number
        transaction count
        swap count
        processing timestamp
        processing latency
    """

    def __init__(
        self,
        database_path: str | Path = "data/market_state.db",
    ):
        self.database_path = Path(
            database_path
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS blocks (
                    block_number INTEGER PRIMARY KEY,
                    transaction_count INTEGER NOT NULL,
                    swap_count INTEGER NOT NULL,
                    processed_at REAL NOT NULL,
                    latency_ms REAL NOT NULL
                )
                """
            )

            connection.commit()

    def save_block(
        self,
        block_number: int,
        transaction_count: int,
        swap_count: int,
        processed_at: float,
        latency_ms: float,
    ) -> None:
        """
        Persist the result of processing one block.
        """

        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO blocks (
                    block_number,
                    transaction_count,
                    swap_count,
                    processed_at,
                    latency_ms
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    block_number,
                    transaction_count,
                    swap_count,
                    processed_at,
                    latency_ms,
                ),
            )

            connection.commit()

    def get_block(
        self,
        block_number: int,
    ) -> dict[str, Any] | None:
        """
        Retrieve persisted information for one block.
        """

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    block_number,
                    transaction_count,
                    swap_count,
                    processed_at,
                    latency_ms
                FROM blocks
                WHERE block_number = ?
                """,
                (block_number,),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def latest_processed_block(self) -> int | None:
        """
        Return the highest block persisted so far.
        """

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT MAX(block_number)
                AS latest_block
                FROM blocks
                """
            ).fetchone()

        if row is None:
            return None

        return row["latest_block"]

    def count_blocks(self) -> int:
        """
        Return the number of persisted blocks.
        """

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM blocks
                """
            ).fetchone()

        return int(row["count"])