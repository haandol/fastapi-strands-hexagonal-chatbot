from typing import TypedDict, Optional, Dict, List, Union, Any


class TextBlock(TypedDict):
    text: str


class ToolUse(TypedDict):
    toolUseId: str
    name: str
    input: Dict[str, Any]


class ToolResult(TypedDict):
    content: List | str


# Content item types for message content
class ToolUseContentItem(TypedDict):
    toolUse: ToolUse


class ToolResultContentItem(TypedDict):
    toolResult: ToolResult


class MessageContent(TypedDict):
    content: Union[
        str,
        List[
            Union[
                TextBlock,
                ToolUseContentItem,
                ToolResultContentItem,
            ]
        ],
    ]


# https://strandsagents.com/latest/documentation/docs/user-guide/concepts/streaming/async-iterators/
class StreamChunk(TypedDict, total=False):
    # Text Generation Events
    delta: Optional[Union[TextBlock, Dict[str, Any]]]  # Raw delta content from the model
    # Lifecycle Events
    message: Optional[MessageContent]  # Present when a new message is created
