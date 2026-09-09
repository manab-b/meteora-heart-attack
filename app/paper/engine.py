from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class PaperPosition:
    id: str
    token: str
    entry_time: str
    entry_price: float
    bin_step_bps: int
    num_bins: int
    min_price: float
    max_price: float
    deposit_sol: float
    fee_rate: float
    lp_share: float
    status: str = "OPEN"
    fees_sol: float = 0.0
    claimed_sol: float = 0.0
    last_price: float = 0.0


class HeartAttackPaper:
    def __init__(self, claim_threshold_sol: float = 0.02, sl_oor_seconds: int = 20):
        self.positions: list[PaperPosition] = []
        self.events: list[dict] = []
        self.claim_threshold_sol = claim_threshold_sol
        self.sl_oor_seconds = sl_oor_seconds

    @staticmethod
    def _range(price: float, bin_step_bps: int, num_bins: int) -> tuple[float, float]:
        if num_bins < 1 or num_bins > 9:
            raise ValueError("num_bins must be between 1 and 9")
        factor = 1 + bin_step_bps / 10000
        half = (num_bins - 1) / 2
        return price * (factor ** -half), price * (factor ** half)

    def open(
        self,
        token: str,
        price: float,
        volume_usd: float,
        bin_step_bps: int = 25,
        num_bins: int = 7,
        deposit_sol: float = 5.0,
        fee_rate: float = 0.013,
        lp_share: float = 0.12,
        reason: str = "volume+breakout-test",
    ) -> str:
        mn, mx = self._range(price, bin_step_bps, num_bins)
        pos = PaperPosition(
            id=f"{token}-{len(self.positions) + 1}",
            token=token,
            entry_time=datetime.now(timezone.utc).isoformat(),
            entry_price=price,
            bin_step_bps=bin_step_bps,
            num_bins=num_bins,
            min_price=mn,
            max_price=mx,
            deposit_sol=deposit_sol,
            fee_rate=fee_rate,
            lp_share=lp_share,
            last_price=price,
        )
        self.positions.append(pos)
        self._log("OPEN", pos, price, volume_usd, reason)
        return pos.id

    def tick(
        self,
        pos_id: str,
        price: float,
        volume_usd_in_range: float,
        seconds_out_of_range: int = 0,
        rug_flags: list[str] | None = None,
    ) -> None:
        pos = self._get(pos_id)
        if pos.status != "OPEN":
            return

        pos.last_price = price
        in_range = pos.min_price <= price <= pos.max_price

        # Temporary estimate. Actual Meteora position fee deltas will override this.
        if in_range and volume_usd_in_range > 0:
            pos.fees_sol += (
                volume_usd_in_range * pos.fee_rate * pos.lp_share
            ) / max(price, 1e-18)

        self._log("TICK", pos, price, volume_usd_in_range)

        if pos.fees_sol - pos.claimed_sol >= self.claim_threshold_sol:
            claimed = pos.fees_sol - pos.claimed_sol
            pos.claimed_sol += claimed
            self._log(
                "CLAIM_TO_SOL",
                pos,
                price,
                volume_usd_in_range,
                f"claimed={claimed:.6f}",
            )

        if rug_flags:
            self.close(pos_id, price, f"RUG_FLAG:{','.join(rug_flags)}")
            return

        if not in_range and seconds_out_of_range >= self.sl_oor_seconds:
            self.close(pos_id, price, "OUT_OF_RANGE")

    def close(self, pos_id: str, price: float, reason: str = "MANUAL") -> None:
        pos = self._get(pos_id)
        if pos.status != "OPEN":
            return

        leftover = pos.fees_sol - pos.claimed_sol
        pos.claimed_sol += leftover
        pos.status = "CLOSED"
        move = (price / pos.entry_price - 1) * 100
        self._log(
            "ZAP_OUT",
            pos,
            price,
            0,
            f"{reason}; move={move:.2f}%; pnl_fees_sol={pos.claimed_sol:.6f}",
        )

    def _get(self, pos_id: str) -> PaperPosition:
        for position in self.positions:
            if position.id == pos_id:
                return position
        raise KeyError(pos_id)

    def _log(
        self,
        action: str,
        pos: PaperPosition,
        price: float,
        volume: float,
        extra: str = "",
    ) -> None:
        self.events.append(
            {
                "time": datetime.now(timezone.utc).isoformat(),
                "action": action,
                "pos_id": pos.id,
                "token": pos.token,
                "price": price,
                "volume": volume,
                "in_range": pos.min_price <= price <= pos.max_price,
                "unclaimed_sol": pos.fees_sol - pos.claimed_sol,
                "claimed_sol": pos.claimed_sol,
                "extra": extra,
            }
        )

    def export(self, path: str = "heart_attack_paper.csv") -> str:
        if not self.events:
            return path
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.events[0].keys())
            writer.writeheader()
            writer.writerows(self.events)
        return str(target)

    def report(self) -> dict:
        closed = [p for p in self.positions if p.status == "CLOSED"]
        total = sum(p.claimed_sol for p in self.positions)
        return {
            "trades": len(self.positions),
            "closed": len(closed),
            "open": len(self.positions) - len(closed),
            "total_claimed_sol": total,
            "avg_claimed_sol": total / len(closed) if closed else 0.0,
            "events": len(self.events),
        }
