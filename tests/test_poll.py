from app.collector.poll import PollLoop

def test_poll_interval_validation():
    try:
        PollLoop(0)
        assert False
    except ValueError:
        assert True
