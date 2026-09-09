from __future__ import annotations
import json,time,urllib.error,urllib.request

class JsonHttpClient:
    def __init__(self,timeout:float=10.0,min_interval:float=0.05,retries:int=3):
        self.timeout=timeout; self.min_interval=min_interval; self.retries=retries; self._last=0.0
    def get(self,url:str):
        last=None
        for attempt in range(self.retries+1):
            wait=self.min_interval-(time.monotonic()-self._last)
            if wait>0: time.sleep(wait)
            try:
                with urllib.request.urlopen(url,timeout=self.timeout) as r:
                    self._last=time.monotonic()
                    if not 200<=r.status<300: raise RuntimeError(f"HTTP {r.status}: {url}")
                    return json.loads(r.read().decode("utf-8"))
            except (urllib.error.URLError,TimeoutError,RuntimeError) as exc:
                last=exc
                if attempt>=self.retries: raise
                time.sleep(min(2.0,0.25*(2**attempt)))
        raise last
