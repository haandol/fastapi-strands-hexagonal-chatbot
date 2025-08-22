import pytest

import adapters.secondary.chat.strands_mcp_agent_adapter as adapter_module
from conftest import DummyRepositorySessionManager, DummyMCPClient


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

    adapter = adapter_module.StrandsMCPAgentAdapter(model_id="m")
    adapter.configure_mcp()

    assert "dummy" in adapter.mcp_clients
    assert client.started is True
    assert adapter.mcp_tools

    session = DummyRepositorySessionManager("s1")
    response = await adapter.generate_response(session, "hi")
    assert response == "dummy"

    stream = await adapter.generate_response_stream(session, "hi")
    events = [e async for e in stream]
    assert events == [{"data": "chunk"}]

    adapter.cleanup()
    assert client.stopped is True
    assert adapter.mcp_clients == {}
    assert adapter.agents == {}
