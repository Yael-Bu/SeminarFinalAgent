# helper.py
import uuid
from typing import List
from langchain_core.messages import AIMessage, SystemMessage, BaseMessage
import random

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


def get_id_signature(student_id: str) -> str:
    """
    Generates a unique, deterministic 3-letter signature based on a shuffled Student ID.
    
    This ensures that each student receives a unique technical namespace (e.g., Table_ABC),
    satisfying the 'Scale' and 'Anti-Cheat' requirements of the simulation[cite: 124].
    """
    # Extract numeric digits
    digits = [d for d in student_id if d.isdigit()]
    
    if not digits:
        return "GEN"
        
    # Seed a local random generator with the full ID for consistency [cite: 102]
    local_random = random.Random(student_id)
    
    # Shuffle the digits to obfuscate the link between the ID and the signature
    shuffled_digits = digits.copy()
    local_random.shuffle(shuffled_digits)
    
    # Take the first 3 digits and map them to letters A-J
    selected_digits = shuffled_digits[:3]
    mapping = {str(i): chr(65 + i) for i in range(10)}
    
    return "".join(mapping.get(d, "X") for d in selected_digits)