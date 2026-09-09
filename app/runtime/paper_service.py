from __future__ import annotations
import sqlite3,time
from app.meteora.collector import collect_once
from app.runtime.health import Health

class PaperService:
    def __init__(self,conn:sqlite3.Connection,client=None,max_pools:int=25):
        self.conn=conn; self.client=client; self.max_pools=max_pools
        self.health=Health(time.time())
    def cycle(self):
        try:
            pools=collect_once(self.conn,self.client,self.max_pools)
            self.health.success(len(pools))
            return pools
        except Exception:
            self.health.error()
            raise
