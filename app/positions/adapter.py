from __future__ import annotations
from typing import Any
from .model import PositionSnapshot

def normalize_position(data: dict[str, Any], observed_at: str, source: str = "meteora") -> PositionSnapshot:
    """Normalize an authoritative Meteora position payload.

    The adapter accepts common aliases but never derives fees from pool volume.
    Missing authoritative fee fields remain zero only when the source explicitly
    reports them as zero; otherwise callers should reject the record.
    """
    def required(*keys: str) -> Any:
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]
        raise ValueError(f"missing required field: {keys}")

    fee_x = required("unclaimed_fee_x", "fee_x", "feeX")
    fee_y = required("unclaimed_fee_y", "fee_y", "feeY")
    return PositionSnapshot(
        position_address=str(required("position_address", "address", "publicKey")),
        owner=str(required("owner", "owner_address", "ownerPublicKey")),
        pool_address=str(required("pool_address", "pool", "lb_pair")),
        lower_bin_id=int(data["lower_bin_id"]) if data.get("lower_bin_id") is not None else None,
        upper_bin_id=int(data["upper_bin_id"]) if data.get("upper_bin_id") is not None else None,
        deposited_x=str(data.get("deposited_x", data.get("total_x_amount", "0"))),
        deposited_y=str(data.get("deposited_y", data.get("total_y_amount", "0"))),
        unclaimed_fee_x=str(fee_x),
        unclaimed_fee_y=str(fee_y),
        observed_at=observed_at,
        source=source,
    )
