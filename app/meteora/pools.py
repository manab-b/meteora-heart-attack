from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable

@dataclass(frozen=True)
class PoolCandidate:
    address: str
    name: str
    tvl_usd: float
    volume_24h_usd: float
    fee_24h_usd: float
    fee_tvl_ratio_24h: float
    current_price: float
    dynamic_fee_pct: float
    bin_step: int
    blacklisted: bool
    token_x_symbol: str
    token_y_symbol: str

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> "PoolCandidate":
        return cls(
            address=str(raw["address"]),
            name=str(raw.get("name") or ""),
            tvl_usd=float(raw.get("tvl") or 0),
            volume_24h_usd=float((raw.get("volume") or {}).get("24h") or 0),
            fee_24h_usd=float((raw.get("fees") or {}).get("24h") or 0),
            fee_tvl_ratio_24h=float((raw.get("fee_tvl_ratio") or {}).get("24h") or 0),
            current_price=float(raw.get("current_price") or 0),
            dynamic_fee_pct=float(raw.get("dynamic_fee_pct") or 0),
            bin_step=int((raw.get("pool_config") or {}).get("bin_step") or 0),
            blacklisted=bool(raw.get("is_blacklisted", False)),
            token_x_symbol=str((raw.get("token_x") or {}).get("symbol") or ""),
            token_y_symbol=str((raw.get("token_y") or {}).get("symbol") or ""),
        )

def select_candidates(pools: Iterable[dict[str, Any]], *,
                      min_tvl_usd: float = 1000,
                      min_volume_24h_usd: float = 10000,
                      exclude_blacklisted: bool = True) -> list[PoolCandidate]:
    candidates = []
    for raw in pools:
        candidate = PoolCandidate.from_api(raw)
        if exclude_blacklisted and candidate.blacklisted:
            continue
        if candidate.tvl_usd < min_tvl_usd or candidate.volume_24h_usd < min_volume_24h_usd:
            continue
        candidates.append(candidate)
    return sorted(candidates, key=lambda p: p.fee_tvl_ratio_24h, reverse=True)
