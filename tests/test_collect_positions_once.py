from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import scripts.collect_positions_once as collect_positions_once


def _args(monkeypatch, db: Path):
    monkeypatch.setattr(
        "sys.argv",
        [
            "collect_positions_once.py",
            "--rpc-url",
            "https://api.mainnet-beta.solana.com",
            "--position-owner",
            "Bd2Qopx5Hs5YxJxfCoGkKPyfsZgR7Ezq7wCXVQo5pcHQ",
            "--pool-address",
            "ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq",
            "--db",
            str(db),
            "--sdk-dir",
            str(Path("sdk")),
        ],
    )


def _discovery_args(monkeypatch, db: Path):
    monkeypatch.setattr(
        "sys.argv",
        [
            "collect_positions_once.py",
            "--rpc-url",
            "https://api.mainnet-beta.solana.com",
            "--position-owner",
            "Bd2Qopx5Hs5YxJxfCoGkKPyfsZgR7Ezq7wCXVQo5pcHQ",
            "--discover-owner-positions",
            "--db",
            str(db),
            "--sdk-dir",
            str(Path("sdk")),
        ],
    )


def test_zero_jsonl_observations_are_failure(monkeypatch, tmp_path: Path):
    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(collect_positions_once.subprocess, "run", lambda *args, **kwargs: Result())
    monkeypatch.setattr(collect_positions_once.Path, "exists", lambda self: True)
    _args(monkeypatch, tmp_path / "meteora.db")

    assert collect_positions_once.main() == 2


def test_jsonl_is_piped_into_existing_position_ingest(monkeypatch, tmp_path: Path):
    payload = {
        "source": "meteora-sdk",
        "observed_at": "2026-09-10T00:00:00.000Z",
        "pool_address": "ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq",
        "owner": "Bd2Qopx5Hs5YxJxfCoGkKPyfsZgR7Ezq7wCXVQo5pcHQ",
        "active_bin_id": 2,
        "active_bin_price": "1.00020001",
        "active_bin_price_ui": 1.00020001,
        "position_address": "11111111111111111111111111111111",
        "lower_bin_id": -5,
        "upper_bin_id": 5,
        "total_x_amount_raw": "100",
        "total_y_amount_raw": "200",
        "fee_x_raw": "3",
        "fee_y_raw": "4",
        "total_claimed_fee_x_raw": "0",
        "total_claimed_fee_y_raw": "0",
        "token_x_mint": "So11111111111111111111111111111111111111112",
        "token_y_mint": "11111111111111111111111111111111",
        "token_x_decimals": 9,
        "token_y_decimals": 9,
    }

    class Result:
        returncode = 0
        stdout = json.dumps(payload) + "\n"
        stderr = ""

    monkeypatch.setattr(collect_positions_once.subprocess, "run", lambda *args, **kwargs: Result())
    monkeypatch.setattr(collect_positions_once.Path, "exists", lambda self: True)
    db = tmp_path / "meteora.db"
    _args(monkeypatch, db)

    assert collect_positions_once.main() == 0

    connection = sqlite3.connect(db)
    try:
        assert connection.execute("SELECT COUNT(*) FROM position_snapshots").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM position_analytics").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM raw_snapshots").fetchone()[0] == 1
    finally:
        connection.close()


def test_wallet_discovery_passes_discovery_flag(monkeypatch, tmp_path: Path):
    class Result:
        returncode = 0
        stdout = ""
        stderr = '{"positions_found":0}\n'

    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return Result()

    monkeypatch.setattr(collect_positions_once.subprocess, "run", fake_run)
    monkeypatch.setattr(collect_positions_once.Path, "exists", lambda self: True)
    _discovery_args(monkeypatch, tmp_path / "meteora.db")

    assert collect_positions_once.main() == 2
    assert "--discover-owner-positions" in calls[0]
    assert "--once" in calls[0]
    assert all("--pool-address" not in item for item in calls[0])
