from __future__ import annotations
from itertools import product
from app.research.strategy_grid import StrategyConfig

def configs(bin_steps=(10,25,50), num_bins=(3,5,7,9),
            min_scores=(0.55,0.60,0.65,0.70), max_drains=(0.40,0.50,0.55)):
    return [StrategyConfig(*x) for x in product(bin_steps,num_bins,min_scores,max_drains)]
