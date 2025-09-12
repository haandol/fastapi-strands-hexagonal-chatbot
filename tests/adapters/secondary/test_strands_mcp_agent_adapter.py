import pytest

import adapters.secondary.mcp_agent.strands_mcp_agent_adapter as adapter_module
from conftest import DummyRepositorySessionManager, DummyMCPClient, DummyO11yAdapter


class DummyClient(DummyMCPClient):
    pass


@pytest.mark.asyncio
async def test_mcp_agent_adapter_lifecycle(monkeypatch):
    client = DummyClient()

    monkeypatch.setattr(
        adapter_module,
        "initialize_mcp_clients",
        lambda cfg: {"dummy": client},
    )
    monkeypatch.setattr(
        adapter_module, "load_mcp_tools", lambda clients: [lambda: None]
    )
    monkeypatch.setattr(adapter_module, "load_mcp_config", lambda: {})

    o11y_adapter = DummyO11yAdapter()
    adapter = adapter_module.StrandsMCPAgentAdapter(
        model_id="m",
        max_tokens=1000,
        temperature=0.3,
        o11y_adapter=o11y_adapter
    )
    adapter.configure_mcp()

    assert "dummy" in adapter.mcp_clients
    assert client.started is True
    assert adapter.mcp_tools

    # Test cleanup
    await adapter.cleanup()
    assert client.stopped is True
    assert adapter.mcp_clients == {}
