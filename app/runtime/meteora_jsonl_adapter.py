from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuntimeObservation:
    pool_address: str
    timestamp: float
    price: float
    active_bin_id: int
    bin_id: int
    x_amount_raw: int
    y_amount_raw: int


def adapt_bin_record(record: dict[str, Any]) -> RuntimeObservation:
    required = ("pool_address", "observed_at", "price", "active_bin_id", "bin_id", "x_amount_raw", "y_amount_raw")
    missing = [key for key in required if key not in record]
    if missing:
        raise ValueError(f"missing SDK fields: {','.join(missing)}")
    return RuntimeObservation(
        pool_address=str(record["pool_address"]),
        timestamp=float(record["observed_at"]),
        price=float(record["price"]),
        active_bin_id=int(record["active_bin_id"]),
        bin_id=int(record["bin_id"]),
        x_amount_raw=int(record["x_amount_raw"]),
        y_amount_raw=int(record["y_amount_raw"]),
    )


def adapt_jsonl(records: list[dict[str, Any]]) -> list[RuntimeObservation]:
    return [adapt_bin_record(record) for record in records if "error" not in record]
