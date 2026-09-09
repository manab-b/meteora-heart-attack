import json

import app.runtime.sdk_bridge as sdk_bridge


def test_run_sdk_once_preserves_environment_and_parses_jsonl(monkeypatch, tmp_path):
    seen = {}

    class Completed:
        stdout = '{"source":"meteora-sdk","pool_address":"P"}\nnot-json\n'
        stderr = "diagnostic\n"
        returncode = 0

    def fake_run(command, **kwargs):
        seen["command"] = command
        seen["env"] = kwargs["env"]
        seen["cwd"] = kwargs["cwd"]
        return Completed()

    monkeypatch.setattr(sdk_bridge.subprocess, "run", fake_run)
    monkeypatch.setenv("RPC_URL", "https://example.invalid")

    result = sdk_bridge.run_sdk_once(
        sdk_dir=tmp_path,
        script="collect",
        args=["POOL"],
        env={"POSITION_OWNER": "OWNER"},
    )

    assert result.ok
    assert result.records == ({"source": "meteora-sdk", "pool_address": "P"},)
    assert result.stderr == "diagnostic\n"
    assert seen["command"] == ["npm", "run", "collect", "--", "--once", "POOL"]
    assert seen["env"]["RPC_URL"] == "https://example.invalid"
    assert seen["env"]["POSITION_OWNER"] == "OWNER"
    assert seen["cwd"] == str(tmp_path)


def test_run_sdk_once_keeps_error_json_from_stdout(monkeypatch, tmp_path):
    class Completed:
        stdout = json.dumps({"error": "rpc unavailable"}) + "\n"
        stderr = ""
        returncode = 1

    monkeypatch.setattr(sdk_bridge.subprocess, "run", lambda *a, **k: Completed())
    result = sdk_bridge.run_sdk_once(sdk_dir=tmp_path, script="collect")

    assert not result.ok
    assert result.returncode == 1
    assert result.records == (("error",),) if False else ({"error": "rpc unavailable"},)
