import sqlite3

from app.collector.position_api_ingest import ingest_position_history_readonly
from app.storage.migrations import initialize_database


class FakeClient:
    def get_position_history(self, position_address):
        return {"position": position_address, "events": [{"type": "claim_fee"}]}


def test_position_history_is_raw_only():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    payload = ingest_position_history_readonly(connection, FakeClient(), "POSITION")

    assert payload["position"] == "POSITION"
    row = connection.execute(
        "SELECT endpoint, status, payload_json FROM raw_snapshots WHERE endpoint LIKE '/positions/%'"
    ).fetchone()
    assert row[0] == "/positions/POSITION/historical"
    assert row[1] == "OK"
    assert "claim_fee" in row[2]
