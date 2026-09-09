from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from app.collector.position_ingest import ingest_jsonl
from app.storage.migrations import initialize_database


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest read-only Meteora SDK position JSONL into SQLite")
    parser.add_argument("input", type=Path)
    parser.add_argument("--db", type=Path, default=Path("meteora.db"))
    args = parser.parse_args()

    connection = sqlite3.connect(args.db)
    try:
        initialize_database(connection)
        with args.input.open("r", encoding="utf-8") as handle:
            results = ingest_jsonl(connection, handle)
        print(json.dumps({"observations": len(results), "database": str(args.db)}))
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
