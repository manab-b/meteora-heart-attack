from pathlib import Path


def test_cli_module_exists():
    path = Path("app/collector/ingest_cli.py")
    assert path.exists()
