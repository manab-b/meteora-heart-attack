from __future__ import annotations
import json
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

@dataclass(frozen=True)
class HttpConfig:
    base_url: str = "https://dlmm.datapi.meteora.ag"
    timeout_seconds: float = 10.0
    max_retries: int = 3
    backoff_seconds: float = 0.5

class MeteoraHttpClient:
    def __init__(self, config: HttpConfig = HttpConfig()):
        self.config = config

    def get_json(self, path: str, params: dict[str, str] | None = None):
        url = self.config.base_url.rstrip("/") + "/" + path.lstrip("/")
        if params:
            from urllib.parse import urlencode
            url += "?" + urlencode(params)
        last_error = None
        for attempt in range(self.config.max_retries + 1):
            try:
                req = Request(url, headers={"Accept": "application/json", "User-Agent": "meteora-heart-attack/1.0"})
                with urlopen(req, timeout=self.config.timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                last_error = exc
                if exc.code not in (429, 500, 502, 503, 504) or attempt >= self.config.max_retries:
                    raise
            except (URLError, TimeoutError) as exc:
                last_error = exc
                if attempt >= self.config.max_retries:
                    raise
            time.sleep(self.config.backoff_seconds * (2 ** attempt))
        raise RuntimeError("Meteora request failed") from last_error
