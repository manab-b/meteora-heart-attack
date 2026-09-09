from __future__ import annotations

import sqlite3

from app.positions.store import init_position_schema
from app.storage.observations import init_observation_schema
from app.storage.raw import init_raw_schema


def initialize_database(connection: sqlite3.Connection) -> None:
    init_observation_schema(connection)
    init_position_schema(connection)
    init_raw_schema(connection)
