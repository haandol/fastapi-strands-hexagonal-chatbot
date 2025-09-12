import pytest

from services.session.session_service import SessionService
from adapters.secondary.session.strands_file_session_adapter import StrandsFileSessionAdapter


@pytest.mark.asyncio
async def test_session_service_lifecycle(tmp_path):
    adapter = StrandsFileSessionAdapter(base_path=str(tmp_path))
    service = SessionService(adapter)

    session_id = await service.create_session("user1")
    session = await service.get_session("user1", session_id)
    assert session is not None

    # Test that we can list messages (even if empty)
    messages = await service.list_messages("user1", session_id)
    assert isinstance(messages, list)

    await service.delete_session("user1", session_id)
