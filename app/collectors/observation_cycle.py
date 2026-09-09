from __future__ import annotations
import sqlite3
from app.adapters.meteora_dlmm import MeteoraDLMMClient
from app.collectors.meteora_collector import MeteoraCollector

class ObservationCycle:
    def __init__(self, client: MeteoraDLMMClient, connection: sqlite3.Connection):
        self.collector=MeteoraCollector(client)
        self.connection=connection

    def run(self, addresses: list[str]) -> int:
        count=0
        for address in addresses:
            obs=self.collector.collect_pool(address)
            # Raw payload is retained separately from derived research observations.
            self.connection.execute(
                "CREATE TABLE IF NOT EXISTS raw_pool_observations (id INTEGER PRIMARY KEY AUTOINCREMENT, pool_address TEXT NOT NULL, observed_at REAL NOT NULL, payload_json TEXT NOT NULL)"
            )
            import json
            self.connection.execute(
                "INSERT INTO raw_pool_observations(pool_address,observed_at,payload_json) VALUES(?,?,?)",
                (obs.address,obs.observed_at,json.dumps(obs.raw,separators=(",",":")))
            )
            count+=1
        self.connection.commit()
        return count
