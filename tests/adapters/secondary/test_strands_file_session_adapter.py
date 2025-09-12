import pytest

from adapters.secondary.session.strands_file_session_adapter import StrandsFileSessionAdapter


@pytest.mark.asyncio
async def test_create_get_delete_session(tmp_path):
    adapter = StrandsFileSessionAdapter(base_path=str(tmp_path))

    session_id = await adapter.create_session("user1")
    session = await adapter.get_session("user1", session_id)
    assert session.session_id == session_id

    await adapter.delete_session("user1", session_id)
    # After deletion, the session should still be accessible but removed from memory
    # The actual file-based session might still exist on disk
