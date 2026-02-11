from typing import TypedDict, List, Annotated, Literal
import operator
from langchain_core.messages import BaseMessage
from production_sim.helper import add_unique_messages


class SimulationState(TypedDict):
    """
    ניהול הזיכרון של הסימולציה.
    """
    messages: Annotated[List[BaseMessage], add_unique_messages]
    current_phase: Literal["development", "production_crash", "debugging", "resolution"]
    scenario_id: str  # איזה תרחיש נבחר רנדומלית
    scenario_data: dict # נתונים ספציפיים לתרחיש (הוראות, רמזים)
    attempts: int # ספירת ניסיונות (אופציונלי לציון)
    welcome_presented: bool # האם הוצג כבר מסר קבלת הפנים למשתמש
    task_presented: bool # האם הוצג כבר המשימה למשתמש
    crash_presented: bool # האם הוצג כבר קריסת הייצור
    last_actor: Literal["team_lead", "architect", None] # מי הפעיל את הצומת האחרון (לניתוב דינמי)