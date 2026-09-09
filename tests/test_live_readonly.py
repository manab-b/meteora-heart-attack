import sqlite3

from app.collector.live_readonly import collect_top_pools_readonly
from app.storage.migrations import initialize_database


class FakeClient:
    def __init__(self):
        self.pool_pages = {
            1: {"data": [{"address": "A"}, {"address": "B"}], "pages": 2},
            2: {"data": [{"address": "C"}, {"address": "D"}], "pages": 2},
        }

    def get_pools(self, *, page, page_size, sort_by=None, query=None, filter_by=None):
        return self.pool_pages[page]

    def get_pool(self, address):
        return {"address": address, "active_bin_id": 100}

    def get_ohlcv(self, address, *, timeframe, start_time=None, end_time=None):
        return {"timeframe": timeframe, "data": []}

    def get_volume_history(self, address):
        return {"data": []}


def test_collect_top_pools_persists_discovery_and_pool_payloads():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    result = collect_top_pools_readonly(connection, FakeClient(), limit=2)

    assert result.discovered == 2
    assert result.attempted == 2
    assert result.succeeded == 2
    assert result.failed == 0
    assert result.pool_addresses == ("A", "B")

    rows = connection.execute(
        "SELECT pool_address, endpoint, status FROM raw_snapshots ORDER BY id"
    ).fetchall()
    assert len(rows) == 7
    assert rows[0][0] is None
    assert all(row[2] == "OK" for row in rows)


def test_collect_top_pools_reads_next_page_when_limit_exceeds_first_page():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    result = collect_top_pools_readonly(connection, FakeClient(), limit=3, page_size=2)

    assert result.discovered == 4
    assert result.attempted == 3
    assert result.succeeded == 3
    assert result.pool_addresses == ("A", "B", "C")

    discovery_rows = connection.execute(
        "SELECT COUNT(*) FROM raw_snapshots WHERE endpoint = '/pools'"
    ).fetchone()[0]
    assert discovery_rows == 2
