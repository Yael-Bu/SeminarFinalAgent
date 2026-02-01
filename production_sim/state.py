from typing import TypedDict, List, Annotated, Literal
import operator
from langchain_core.messages import BaseMessage

class SimulationState(TypedDict):
    """
    ניהול הזיכרון של הסימולציה.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    current_phase: Literal["development", "production_crash", "debugging", "resolution"]
    scenario_id: str  # איזה תרחיש נבחר רנדומלית
    scenario_data: dict # נתונים ספציפיים לתרחיש (הוראות, רמזים)
    attempts: int # ספירת ניסיונות (אופציונלי לציון)