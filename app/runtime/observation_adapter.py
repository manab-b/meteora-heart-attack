from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class ObservationState:
    pool_address:str
    strategy_key:str
    timestamp:float
    price:float
    drain_score:float
    fee_velocity:float
    range_survival:float
    eligible:bool=True
def adapt(raw:dict,strategy_key:str)->ObservationState:
    return ObservationState(
        pool_address=str(raw["pool_address"]), strategy_key=strategy_key,
        timestamp=float(raw["timestamp"]), price=float(raw["price"]),
        drain_score=float(raw["drain_score"]), fee_velocity=float(raw["fee_velocity"]),
        range_survival=float(raw["range_survival"]), eligible=bool(raw.get("eligible",True)))
