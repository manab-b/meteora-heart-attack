from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RangeState:
    active_bin_id:int
    lower_bin_id:int
    upper_bin_id:int
    liquidity_drain:float=0.0

    @property
    def in_range(self)->bool:
        return self.lower_bin_id <= self.active_bin_id <= self.upper_bin_id

    @property
    def distance_to_lower(self)->int:
        return self.active_bin_id-self.lower_bin_id

    @property
    def distance_to_upper(self)->int:
        return self.upper_bin_id-self.active_bin_id

def from_position(active_bin_id:int,lower_bin_id:int|None,upper_bin_id:int|None,liquidity_drain:float=0.0)->RangeState|None:
    if lower_bin_id is None or upper_bin_id is None: return None
    if lower_bin_id>upper_bin_id: raise ValueError("lower_bin_id must be <= upper_bin_id")
    return RangeState(active_bin_id,lower_bin_id,upper_bin_id,max(0.0,min(1.0,liquidity_drain)))
