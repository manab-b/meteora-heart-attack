from __future__ import annotations
import hashlib
def observation_key(pool_address:str,observed_at:float)->str:
    raw=f"{pool_address}:{observed_at:.6f}".encode()
    return hashlib.sha256(raw).hexdigest()
def trade_key(pool_address:str,strategy_key:str,entry_at:float)->str:
    raw=f"{pool_address}:{strategy_key}:{entry_at:.6f}".encode()
    return hashlib.sha256(raw).hexdigest()
