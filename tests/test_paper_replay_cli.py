import sqlite3

import pytest

from app.research.paper_replay_cli import run


_REQUIRED_TABLES = (
    "position_analytics",
    "position_snapshots",
    "bin_liquidity_snapshots",
    "bin_drain_events",
    "token_quotes",
    "raw_snapshots",
)


def _empty_database(path):
    connection = sqlite3.connect(path)
    for table in _REQUIRED_TABLES:
        connection.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)")
    connection.commit()
    connection.close()


def test_cli_completion_gate_rejects_replay_without_paper_trade(tmp_path):
    path = tmp_path / "empty.sqlite"
    _empty_database(path)

    with pytest.raises(ValueError, match="no closed paper trades"):
        run(path, require_paper_trades=True)


def test_cli_allows_dataset_audit_without_completion_gate(tmp_path):
    path = tmp_path / "empty.sqlite"
    _empty_database(path)

    result = run(path)

    assert result["positions_replayed"] == 0
    assert result["paper_trades"] == 0
