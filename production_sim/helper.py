# helper.py
import uuid
from typing import List
from langchain_core.messages import AIMessage, SystemMessage, BaseMessage

def create_ai_message(content: str) -> AIMessage:
    """
    Return an AIMessage with a unique ID for tracking.
    """
    return AIMessage(
        content=content,
        additional_kwargs={"id": str(uuid.uuid4())}
    )

def create_sys_message(content: str) -> SystemMessage:
    """
    Return a SystemMessage with a unique ID for tracking.
    """
    return SystemMessage(
        content=content,
        additional_kwargs={"id": str(uuid.uuid4())}
    )

def ensure_id(msg):
    if not getattr(msg, "id", None):
        msg.id = str(uuid.uuid4())
    return msg

def add_unique_messages(
    existing: List[BaseMessage],
    new: List[BaseMessage]
) -> List[BaseMessage]:
    
    seen_ids = {m.id for m in existing if getattr(m, "id", None)}

    unique_new = [
        m for m in new
        if getattr(m, "id", None) not in seen_ids
    ]

    return existing + unique_new