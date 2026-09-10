import json
import sqlite3

from app.collector.bin_ingest_cli import main
from app.storage.migrations import initialize_database


def test_bin_ingest_cli_persists_real_shape_jsonl(tmp_path, monkeypatch, capsys):
    input_path = tmp_path / "bins.jsonl"
    db_path = tmp_path / "meteora.sqlite"
    input_path.write_text(
        json.dumps(
            {
                "observed_at": "2026-09-09T12:00:00+00:00",
                "pool_address": "POOL",
                "bin_id": 10,
                "active_bin_id": 10,
                "price": "1.0",
                "x_amount_raw": "100",
                "y_amount_raw": "50",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        ["bin_ingest_cli", str(input_path), "--db", str(db_path)],
    )

    assert main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["observations"] == 1

    connection = sqlite3.connect(db_path)
    try:
        initialize_database(connection)
        assert connection.execute("SELECT COUNT(*) FROM bin_liquidity_snapshots").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM raw_snapshots").fetchone()[0] == 1
    finally:
        connection.close()
