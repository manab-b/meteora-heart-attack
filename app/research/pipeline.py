from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from app.research.backtest_runner import BacktestRunner
from app.research.backtest_report import build_report
from app.research.walk_forward import rolling_folds
from app.research.monte_carlo import run as monte_carlo

@dataclass(frozen=True)
class PipelineConfig:
    train_size:int
    test_size:int
    step:int|None=None
    monte_carlo_runs:int=10_000

@dataclass(frozen=True)
class FoldReport:
    train_count:int
    test_count:int
    result_count:int

@dataclass(frozen=True)
class PipelineReport:
    tested:int
    ranked:Any
    folds:list[FoldReport]

class ResearchPipeline:
    def __init__(self, simulator:Callable, config:PipelineConfig):
        self.runner=BacktestRunner(simulator); self.config=config

    def run(self, ticks:list[Any], strategy_configs=None)->PipelineReport:
        folds=rolling_folds(ticks,self.config.train_size,self.config.test_size,self.config.step)
        fold_reports=[]
        all_results=[]
        for fold in folds:
            report=build_report(self.runner.run(fold.test,strategy_configs).results)
            all_results.extend(report.ranked)
            fold_reports.append(FoldReport(len(fold.train),len(fold.test),report.tested))
        final=build_report(all_results)
        return PipelineReport(final.tested,final.ranked,fold_reports)
