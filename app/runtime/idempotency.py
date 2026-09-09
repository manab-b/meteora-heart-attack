from __future__ import annotations

import hashlib


def _key(*parts: object) -> str:
    raw = ":".join(str(part) for part in parts).encode()
    return hashlib.sha256(raw).hexdigest()


def observation_key(pool_address: str, observed_at: float) -> str:
    """Backward-compatible pool-level observation key."""
    return _key(pool_address, f"{observed_at:.6f}")


def bin_observation_key(pool_address: str, bin_id: int, observed_at: float) -> str:
    return _key("bin", pool_address, int(bin_id), f"{observed_at:.6f}")


def position_observation_key(pool_address: str, position_address: str, observed_at: float) -> str:
    return _key("position", pool_address, position_address, f"{observed_at:.6f}")


def trade_key(pool_address: str, strategy_key: str, entry_at: float) -> str:
    return _key(pool_address, strategy_key, f"{entry_at:.6f}")
