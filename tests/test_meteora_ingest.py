import sqlite3

from app.collector.meteora_ingest import ingest_pool_readonly
from app.storage.migrations import initialize_database


class FakeClient:
    def get_pool(self, address):
        return {"address": address, "active_bin_id": 123}

    def get_ohlcv(self, address, *, timeframe, start_time, end_time):
        return {"timeframe": timeframe, "data": [{"timestamp": start_time or 1, "close": 2.0}]}

    def get_volume_history(self, address):
        return {"data": [{"timestamp": 1, "volume": 100.0}]}


def test_ingest_persists_raw_api_payloads_without_derivation():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    result = ingest_pool_readonly(connection, FakeClient(), "POOL", start_time=100, end_time=200)

    assert result["pool"]["active_bin_id"] == 123
    rows = connection.execute(
        "SELECT endpoint, status, payload_json FROM raw_snapshots WHERE pool_address = ? ORDER BY id",
        ("POOL",),
    ).fetchall()
    assert len(rows) == 3
    assert all(row[1] == "OK" for row in rows)
    assert "active_bin_id" in rows[0][2]
