from __future__ import annotations
import csv

FIELDS = [
    "bins","min_volume_usd","min_fee_velocity_sol_min","max_drain_score",
    "min_range_survival_seconds","out_of_range_seconds",
    "fee_velocity_floor_sol_min","trades","median_fee_sol",
    "total_fee_sol","median_hold_seconds","max_drawdown_sol"
]

def export_csv(rows: list[dict], path: str) -> str:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path
