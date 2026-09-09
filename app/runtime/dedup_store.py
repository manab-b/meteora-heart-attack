from __future__ import annotations
import sqlite3
class DedupStore:
    def __init__(self,conn):
        self.conn=conn
        self.conn.execute("CREATE TABLE IF NOT EXISTS runtime_keys(key TEXT PRIMARY KEY, created_at REAL NOT NULL)")
        self.conn.commit()
    def claim(self,key:str,created_at:float)->bool:
        cur=self.conn.execute("INSERT OR IGNORE INTO runtime_keys(key,created_at) VALUES(?,?)",(key,created_at))
        self.conn.commit()
        return cur.rowcount==1
