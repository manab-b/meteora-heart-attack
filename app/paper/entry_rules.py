from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PaperDecision:
    action: str
    reason: str

def decide_entry(*, score: float, min_score: float, already_open: bool) -> PaperDecision:
    if already_open: return PaperDecision("HOLD","ALREADY_OPEN")
    if score < min_score: return PaperDecision("HOLD","SCORE_BELOW_THRESHOLD")
    return PaperDecision("OPEN","SCORE_OK")
