from __future__ import annotations
from dataclasses import dataclass
import time

@dataclass(frozen=True)
class Experiment:
    id: str
    pool_address: str
    train_start: float
    train_end: float
    test_start: float
    test_end: float
    strategy_count: int
    created_at: float

def create_experiment(pool_address:str, train_start:float, train_end:float,
                      test_start:float, test_end:float, strategy_count:int)->Experiment:
    return Experiment(f"{pool_address}:{int(time.time()*1000)}",pool_address,
                      train_start,train_end,test_start,test_end,strategy_count,time.time())
