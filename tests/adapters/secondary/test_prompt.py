from adapters.secondary.chat.prompt import SYSTEM_PROMPT


def test_system_prompt_defined():
    assert isinstance(SYSTEM_PROMPT, str)
    assert SYSTEM_PROMPT
