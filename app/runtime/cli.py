from __future__ import annotations
import argparse
from app.runtime.research_runner import ResearchRuntime

def build_parser():
    p=argparse.ArgumentParser(description="Meteora Heart Attack research runner")
    p.add_argument("--interval",type=int,default=30)
    p.add_argument("--iterations",type=int,default=None)
    return p

def main():
    args=build_parser().parse_args()
    # Wiring is deliberately dependency-injected; live adapters remain read-only.
    def collect(): return None
    def cycle(): return None
    ResearchRuntime(collect=collect,cycle=cycle,interval_seconds=args.interval,
                    max_iterations=args.iterations).run()

if __name__=="__main__":
    main()
