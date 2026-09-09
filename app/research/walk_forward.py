from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Fold:
    train: tuple[float, ...]
    test: tuple[float, ...]

def rolling_folds(values: list[float], train_size: int, test_size: int, step: int | None = None) -> list[Fold]:
    if train_size < 1 or test_size < 1: raise ValueError("sizes must be positive")
    step = step or test_size
    if step < 1: raise ValueError("step must be positive")
    out=[]
    start=0
    while start + train_size + test_size <= len(values):
        out.append(Fold(tuple(values[start:start+train_size]),
                        tuple(values[start+train_size:start+train_size+test_size])))
        start += step
    return out
