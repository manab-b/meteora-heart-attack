from __future__ import annotations
import time, urllib.request, json

class JsonHttpClient:
    def __init__(self, timeout:float=10.0, min_interval:float=0.05):
        self.timeout=timeout; self.min_interval=min_interval; self._last=0.0
    def get(self,url:str):
        wait=self.min_interval-(time.monotonic()-self._last)
        if wait>0: time.sleep(wait)
        with urllib.request.urlopen(url,timeout=self.timeout) as r:
            self._last=time.monotonic()
            if r.status<200 or r.status>=300: raise RuntimeError(f"HTTP {r.status}: {url}")
            return json.loads(r.read().decode("utf-8"))
