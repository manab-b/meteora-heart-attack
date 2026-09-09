from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SolanaRpcConfig:
    url: str
    timeout_seconds: float = 15.0


class SolanaReadonlyRpc:
    """Minimal JSON-RPC reader. It has no signing or transaction methods by design."""

    def __init__(self, config: SolanaRpcConfig) -> None:
        if not config.url:
            raise ValueError("RPC URL is required")
        self.config = config

    def call(self, method: str, params: list[Any] | None = None) -> Any:
        request_body = json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
        ).encode("utf-8")
        request = urllib.request.Request(
            self.config.url,
            data=request_body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if "error" in payload:
            raise RuntimeError(f"Solana RPC error: {payload['error']}")
        return payload.get("result")

    def get_account_info(self, address: str, *, encoding: str = "base64") -> Any:
        return self.call("getAccountInfo", [address, {"encoding": encoding}])

    def get_multiple_accounts(self, addresses: list[str], *, encoding: str = "base64") -> Any:
        return self.call("getMultipleAccounts", [addresses, {"encoding": encoding}])

    def get_slot(self) -> int:
        return int(self.call("getSlot", [{"commitment": "confirmed"}]))
