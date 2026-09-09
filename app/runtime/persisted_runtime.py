from __future__ import annotations
import sqlite3
from app.runtime.paper_persistence import init,save_open,save_closed
class PersistedLedger:
    def __init__(self,conn=None):
        self.conn=conn or sqlite3.connect(":memory:")
        init(self.conn)
    def open(self,t): save_open(self.conn,t)
    def close(self,c): save_closed(self.conn,c)
