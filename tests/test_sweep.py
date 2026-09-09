from app.research.sweep import run_sweep
from app.strategy.backtest import Observation

def test_sweep_produces_results():
    xs = [Observation(i, 1, 200_000, .05, .1, 120, True) for i in range(20)]
    rows = run_sweep({3: xs}, bins_values=(3,), volume_values=(100_000,),
                     fee_values=(.01,), drain_values=(.2,),
                     survival_values=(60,), oor_values=(20,),
                     floor_values=(.001,))
    assert len(rows) == 1
    assert rows[0]["bins"] == 3
