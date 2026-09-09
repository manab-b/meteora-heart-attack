from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class RunnerConfig:
    enabled:bool=True

class PipelineRunner:
    def __init__(self, discovery:Callable[[],object], paper_cycle:Callable[[],int], research:Callable[[],object]):
        self.discovery=discovery; self.paper_cycle=paper_cycle; self.research=research

    def run_once(self):
        discovered=self.discovery()
        ticks=self.paper_cycle()
        report=self.research()
        return {"discovery":discovered,"paper_ticks":ticks,"research":report}
