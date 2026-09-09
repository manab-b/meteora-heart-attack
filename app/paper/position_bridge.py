from __future__ import annotations

from app.metrics.bin_drain import BinDrainSignal, classify_bin_drain
from app.metrics.bin_liquidity import BinLiquiditySnapshot
from app.paper.range_state import RangeState, from_position
from app.positions.model import PositionSnapshot


def range_from_position(snapshot: PositionSnapshot, active_bin_id: int) -> RangeState | None:
    return from_position(active_bin_id, snapshot.lower_bin_id, snapshot.upper_bin_id)


def drain_from_snapshots(
    pool_address: str,
    previous_active_bin_id: int,
    current_active_bin_id: int,
    previous: BinLiquiditySnapshot,
    current: BinLiquiditySnapshot,
) -> BinDrainSignal:
    if previous.bin_id != current.bin_id:
        raise ValueError("bin snapshots must match")
    return classify_bin_drain(
        pool_address=pool_address,
        bin_id=current.bin_id,
        previous_active_bin_id=previous_active_bin_id,
        current_active_bin_id=current_active_bin_id,
        previous_x_raw=previous.x_amount_raw,
        previous_y_raw=previous.y_amount_raw,
        current_x_raw=current.x_amount_raw,
        current_y_raw=current.y_amount_raw,
        elapsed_seconds=current.observed_at - previous.observed_at,
    )


def fee_delta(previous: PositionSnapshot, current: PositionSnapshot) -> tuple[float, float]:
    if previous.position_address != current.position_address:
        raise ValueError("position snapshots must match")
    return (
        current.unclaimed_fee_x_float - previous.unclaimed_fee_x_float,
        current.unclaimed_fee_y_float - previous.unclaimed_fee_y_float,
    )
