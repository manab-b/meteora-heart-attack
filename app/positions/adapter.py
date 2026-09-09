from __future__ import annotations

from typing import Any

from .model import PositionSnapshot


def normalize_position(data: dict[str, Any], observed_at: str, source: str = "meteora") -> PositionSnapshot:
    """Normalize an authoritative Meteora position payload.

    The adapter accepts common SDK/raw aliases but never derives fees from pool
    volume. Raw on-chain amounts remain strings until a valuation layer converts
    them using explicit token decimals.
    """
    def required(*keys: str) -> Any:
        for key in keys:
            if key in data and data[key] is not None:
                return data[key]
        raise ValueError(f"missing required field: {keys}")

    fee_x = required("unclaimed_fee_x", "fee_x", "feeX", "fee_x_raw")
    fee_y = required("unclaimed_fee_y", "fee_y", "feeY", "fee_y_raw")
    deposited_x = required("deposited_x", "total_x_amount", "total_x_amount_raw")
    deposited_y = required("deposited_y", "total_y_amount", "total_y_amount_raw")
    return PositionSnapshot(
        position_address=str(required("position_address", "address", "publicKey")),
        owner=str(required("owner", "owner_address", "ownerPublicKey")),
        pool_address=str(required("pool_address", "pool", "lb_pair")),
        lower_bin_id=int(data["lower_bin_id"]) if data.get("lower_bin_id") is not None else None,
        upper_bin_id=int(data["upper_bin_id"]) if data.get("upper_bin_id") is not None else None,
        deposited_x=str(deposited_x),
        deposited_y=str(deposited_y),
        unclaimed_fee_x=str(fee_x),
        unclaimed_fee_y=str(fee_y),
        observed_at=observed_at,
        source=source,
    )
