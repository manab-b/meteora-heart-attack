from app.strategy.entry import should_enter, EntryConfig
from app.strategy.exit import should_exit

def test_entry_requires_all_filters():
    cfg = EntryConfig()
    assert should_enter(200000, .02, .1, 120, cfg)
    assert not should_enter(200000, .02, .8, 120, cfg)

def test_exit_on_drain():
    assert should_exit(True, 0, .8, .1)[0]
