from __future__ import annotations
from app.paper.market_tick import MarketTick

class PaperBridge:
    def __init__(self, engine):
        self.engine=engine
        self.positions: dict[str,str]={}

    def open(self, token: str, price: float, volume_usd: float, **kwargs) -> str:
        pid=self.engine.open(token,price,volume_usd,**kwargs)
        self.positions[token]=pid
        return pid

    def tick(self, token: str, tick: MarketTick) -> None:
        pid=self.positions.get(token)
        if pid is None: return
        self.engine.tick(pid,tick.price,tick.volume_usd_in_range,
                          tick.seconds_out_of_range,tick.rug_flags)
        pos=self.engine._get(pid)
        if pos.status != "OPEN":
            self.positions.pop(token,None)
