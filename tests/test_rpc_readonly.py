import pytest

from app.collector.rpc_readonly import SolanaReadonlyRpc, SolanaRpcConfig


def test_rpc_adapter_is_read_only_surface():
    rpc = SolanaReadonlyRpc(SolanaRpcConfig("https://example.invalid"))
    assert hasattr(rpc, "get_account_info")
    assert hasattr(rpc, "get_multiple_accounts")
    assert hasattr(rpc, "get_slot")
    assert not hasattr(rpc, "send_transaction")
    assert not hasattr(rpc, "sign_transaction")


def test_rpc_requires_url():
    with pytest.raises(ValueError, match="RPC URL"):
        SolanaReadonlyRpc(SolanaRpcConfig(""))
