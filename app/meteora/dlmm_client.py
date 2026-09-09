from __future__ import annotations
from app.infra.http_client import JsonHttpClient

BASE_URL="https://dlmm.datapi.meteora.ag"

class DlmmDataClient:
    def __init__(self,http:JsonHttpClient|None=None,base_url:str=BASE_URL):
        self.http=http or JsonHttpClient(); self.base_url=base_url.rstrip("/")
    def pools(self, **params):
        url=self.base_url+"/pools"
        if params: url += "?" + "&".join(f"{k}={v}" for k,v in params.items())
        return self.http.get(url)
    def ohlcv(self,address:str,**params):
        url=f"{self.base_url}/pools/{address}/ohlcv"
        if params: url += "?" + "&".join(f"{k}={v}" for k,v in params.items())
        return self.http.get(url)
    def volume_history(self,address:str,**params):
        url=f"{self.base_url}/pools/{address}/volume/history"
        if params: url += "?" + "&".join(f"{k}={v}" for k,v in params.items())
        return self.http.get(url)
