from __future__ import annotations
import argparse
import time
import sqlite3
from app.meteora.client import MeteoraClient
from app.collector.rest import fetch_pool_tick
from app.storage.ticks import init_tick_schema, insert_tick

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", action="append", required=True)
    parser.add_argument("--interval", type=float, default=30.0)
    parser.add_argument("--db", default="data/heart_attack.sqlite3")
    args = parser.parse_args()

    client = MeteoraClient()
    connection = sqlite3.connect(args.db)
    init_tick_schema(connection)

    try:
        while True:
            started = time.monotonic()
            for pool_address in args.pool:
                try:
                    tick = fetch_pool_tick(client, pool_address)
                    insert_tick(connection, tick)
                    print(pool_address, tick.observed_at, tick.price, tick.active_bin)
                except Exception as exc:
                    print(pool_address, "ERROR", repr(exc))
            elapsed = time.monotonic() - started
            time.sleep(max(0.0, args.interval - elapsed))
    except KeyboardInterrupt:
        pass
    finally:
        connection.close()

if __name__ == "__main__":
    main()
