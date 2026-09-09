from __future__ import annotations
import math

def constant_product_il(entry_price: float, current_price: float) -> float:
    if entry_price <= 0 or current_price <= 0:
        raise ValueError("prices must be positive")
    ratio = current_price / entry_price
    return 2 * math.sqrt(ratio) / (1 + ratio) - 1

def impermanent_loss_pct(entry_price: float, current_price: float) -> float:
    return constant_product_il(entry_price, current_price) * 100.0
