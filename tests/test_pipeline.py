import sqlite3
from app.storage.migrations import initialize_database
from app.collector.pipeline import CollectorPipeline
from app.positions.model import PositionSnapshot

def test_pipeline_persists_position():
    db = sqlite3.connect(":memory:")
    initialize_database(db)
    p = PositionSnapshot("p","o","pool",1,3,"1","2","0.1","0.2",
                         "2026-01-01T00:00:00+00:00","test")
    assert CollectorPipeline(db).persist_position(p)
    assert db.execute("select count(*) from position_snapshots").fetchone()[0] == 1
