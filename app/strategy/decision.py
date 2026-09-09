from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Decision:
    action: str
    score: float
    reasons: tuple[str, ...]

def decide(score: float, drain_score: float, freshness_ok: bool,
           min_score: float = 0.65, max_drain: float = 0.55) -> Decision:
    reasons=[]
    if not freshness_ok: return Decision("IGNORE",score,("STALE_DATA",))
    if drain_score >= max_drain: return Decision("IGNORE",score,("LIQUIDITY_DRAIN",))
    if score >= min_score:
        reasons.append("SCORE_OK")
        if drain_score > 0: reasons.append("DRAIN_MONITORED")
        return Decision("ENTER",score,tuple(reasons))
    return Decision("IGNORE",score,("SCORE_LOW",))
