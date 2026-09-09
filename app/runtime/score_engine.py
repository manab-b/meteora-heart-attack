from __future__ import annotations
def score_state(*,drain_score:float,fee_velocity:float,range_survival:float,drain_weight:float=1.0,fee_weight:float=1.0,range_weight:float=1.0)->dict:
    score=drain_score*drain_weight+fee_velocity*fee_weight+range_survival*range_weight
    return {"score":score,"components":{"drain":drain_score,"fee_velocity":fee_velocity,"range_survival":range_survival}}
def eligible_state(*,score:float,min_score:float=1.0,range_survival:float=1.0,fee_velocity:float=0.0)->bool:
    return score>=min_score and range_survival>0 and fee_velocity>=0
