from __future__ import annotations
import time
from app.meteora.adapter import normalize_ohlcv
from app.paper.state_tracker import StateTracker
from app.paper.live_processor import LivePaperProcessor

class PaperCycle:
    def __init__(self,conn,client,processor_factory):
        self.conn=conn; self.client=client; self.processor_factory=processor_factory
        self.trackers={}; self.processors={}

    def process_pool(self,pool_address:str,score:float,min_price:float,max_price:float):
        payload=self.client.ohlcv(pool_address)
        ticks=normalize_ohlcv(payload,time.time())
        tracker=self.trackers.setdefault(pool_address,StateTracker())
        processor=self.processors.setdefault(pool_address,self.processor_factory(self.conn))
        results=[]
        for tick in ticks:
            state=tracker.update(tick)
            results.append(processor.process(pool_address,tick,state,score,min_price,max_price))
        return results
