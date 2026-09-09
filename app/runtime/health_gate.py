from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class HealthGate:
    max_errors:int=3
    max_stale_seconds:float=120.0
def allow_new_entries(snapshot,now,gate=HealthGate()):
    runtime=snapshot["runtime"]
    return runtime["healthy"] and runtime["errors"]<=gate.max_errors and now-runtime["last_success_at"]<=gate.max_stale_seconds
