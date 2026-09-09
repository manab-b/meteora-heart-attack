from __future__ import annotations
from dataclasses import asdict
def report(checkpoint,cycle_result):
    return {
      "healthy":checkpoint.healthy,
      "cycles":checkpoint.cycles,
      "errors":checkpoint.errors,
      "last_success_at":checkpoint.last_success_at,
      "last_error":checkpoint.last_error,
      "pools":cycle_result.pools,
      "observations":cycle_result.observations,
      "trades_closed":cycle_result.trades_closed,
    }
