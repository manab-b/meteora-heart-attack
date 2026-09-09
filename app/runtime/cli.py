from __future__ import annotations
import argparse,time
def build_parser():
    p=argparse.ArgumentParser(); p.add_argument("--once",action="store_true"); p.add_argument("--interval",type=float,default=30.0); return p
def run(orchestrator,checkpoint,price_provider,size_sol=1.0,interval=30.0,once=False):
    while True:
        started=time.monotonic(); now=time.time()
        try: result=orchestrator.run_once(now,price_provider,size_sol); checkpoint.success(now)
        except Exception as exc: checkpoint.failure(exc); result=None
        if once: return result
        time.sleep(max(0,interval-(time.monotonic()-started)))
