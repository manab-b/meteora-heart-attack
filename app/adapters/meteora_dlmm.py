from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import time
import urllib.request
import json

BASE_URL="https://dlmm.datapi.meteora.ag"

@dataclass(frozen=True)
class ApiResponse:
    path: str
    fetched_at: float
    data: Any

class MeteoraDLMMClient:
    def __init__(self, base_url: str=BASE_URL, timeout: float=10.0):
        self.base_url=base_url.rstrip("/")
        self.timeout=timeout

    def get(self, path: str, params: dict[str,str|int|float]|None=None) -> ApiResponse:
        query=""
        if params:
            from urllib.parse import urlencode
            query="?"+urlencode(params)
        req=urllib.request.Request(self.base_url+path+query, headers={"Accept":"application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            data=json.loads(response.read().decode("utf-8"))
        return ApiResponse(path,time.time(),data)

    def pools(self, **params):
        return self.get("/pools", params)

    def pool(self, address: str):
        return self.get(f"/pools/{address}")

    def ohlcv(self, address: str, **params):
        return self.get(f"/pools/{address}/ohlcv", params)

    def volume_history(self, address: str, **params):
        return self.get(f"/pools/{address}/volume/history", params)
