from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import scripts.collect_bins_once as collect_bins_once


def _args(monkeypatch, db: Path):
    monkeypatch.setattr(
        "sys.argv",
        [
            "collect_bins_once.py",
            "--rpc-url",
            "https://api.mainnet-beta.solana.com",
            "--pool-address",
            "ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq",
            "--lower-bin-id",
            "-5",
            "--upper-bin-id",
            "5",
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

    monkeypatch.setattr(collect_bins_once.subprocess, "run", lambda *args, **kwargs: Result())
    monkeypatch.setattr(collect_bins_once.Path, "exists", lambda self: True)
    _args(monkeypatch, tmp_path / "meteora.db")

    assert collect_bins_once.main() == 2


def test_jsonl_is_piped_into_existing_bin_ingest(monkeypatch, tmp_path: Path):
    payload = {
        "source": "meteora-sdk",
        "observed_at": "2026-09-10T00:00:00.000Z",
        "pool_address": "ARwi1S4DaiTG5DX7S4M4ZsrXqpMD1MrTmbu9ue2tpmEq",
        "active_bin_id": 2,
        "bin_id": 2,
        "price": "1.0",
        "x_amount_raw": "100",
        "y_amount_raw": "200",
    }

    class Result:
        returncode = 0
        stdout = json.dumps(payload) + "\n"
        stderr = ""

    monkeypatch.setattr(collect_bins_once.subprocess, "run", lambda *args, **kwargs: Result())
    monkeypatch.setattr(collect_bins_once.Path, "exists", lambda self: True)
    db = tmp_path / "meteora.db"
    _args(monkeypatch, db)

    assert collect_bins_once.main() == 0

    connection = sqlite3.connect(db)
    try:
        assert connection.execute("SELECT COUNT(*) FROM bin_liquidity_snapshots").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM raw_snapshots").fetchone()[0] == 1
    finally:
        connection.close()
