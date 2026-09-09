from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class Checkpoint:
    cycle: int = 0
    last_pool: str | None = None
    last_observed_at: str | None = None

def load(path: str) -> Checkpoint:
    p=Path(path)
    if not p.exists(): return Checkpoint()
    return Checkpoint(**json.loads(p.read_text()))

def save(path: str, checkpoint: Checkpoint) -> None:
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    tmp=p.with_suffix(p.suffix+".tmp")
    tmp.write_text(json.dumps(asdict(checkpoint), separators=(",",":")))
    tmp.replace(p)
