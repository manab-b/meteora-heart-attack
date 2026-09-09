from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Fold:
    train: list[Any]
    test: list[Any]

def rolling_folds(ticks: list[Any], train_size: int, test_size: int, step: int|None=None) -> list[Fold]:
    if train_size<=0 or test_size<=0: raise ValueError("window sizes must be positive")
    step=step or test_size
    out=[]; start=0
    while start+train_size+test_size<=len(ticks):
        out.append(Fold(ticks[start:start+train_size],ticks[start+train_size:start+train_size+test_size]))
        start+=step
    return out
