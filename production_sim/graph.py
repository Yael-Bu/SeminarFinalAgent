from langgraph.graph import StateGraph, END
from .state import SimulationState
from .agents import AgentNodes
from .scenarios import ScenarioManager

class ProductionTrapSim:
    def __init__(self):
        self.nodes = AgentNodes()
        self.scenario_manager = ScenarioManager()
        self.workflow = StateGraph(SimulationState)
        
        self._build_graph()

    def _build_graph(self):
        # 1. Add Nodes
        self.workflow.add_node("team_lead", self.nodes.team_lead_node)
        self.workflow.add_node("production_monitor", self.nodes.production_monitor_node)
        self.workflow.add_node("architect", self.nodes.architect_node)

        # 2. Set Entry Point
        self.workflow.set_entry_point("team_lead")

        # 3. Conditional Edges (The Routing Logic)
        
        # אחרי שהראש צוות מדבר:
        # אם אנחנו עדיין בפיתוח -> תעצור (END) ותחכה למשתמש.
        # אם הקוד אושר והתרסק -> תעבור מיד לניטור (Production Monitor).
        self.workflow.add_conditional_edges(
            "team_lead",
            self._route_after_dev,
            {
                "wait_for_user": END,            # <--- השינוי הקריטי: עצירה למשתמש
                "trigger_crash": "production_monitor"
            }
        )

        # אחרי שהניטור מדבר (התרעת שגיאה), עוברים לארכיטקט
        self.workflow.add_edge("production_monitor", "architect")

        # אחרי שהארכיטקט מדבר:
        # בין אם פתרנו ובין אם נכשלנו -> תעצור (END) ותחכה למשתמש.
        self.workflow.add_conditional_edges(
            "architect",
            self._route_after_debug,
            {
                "wait_for_user": END,            # <--- השינוי הקריטי: עצירה למשתמש
                "finished": END
            }
        )

    def _route_after_dev(self, state):
        # אם הפאזה היא "התרסקות", עוברים לניטור. אחרת עוצרים ומחכים.
        if state["current_phase"] == "production_crash":
            return "trigger_crash"
        return "wait_for_user"

    def _route_after_debug(self, state):
        # הארכיטקט תמיד מחזיר שליטה למשתמש, אלא אם כן סיימנו
        if state["current_phase"] == "resolution":
            return "finished"
        return "wait_for_user"

    def compile(self):
        return self.workflow.compile()
        
    def get_initial_state(self):
        scenario = self.scenario_manager.get_random_scenario()
        return {
            "messages": [],
            "current_phase": "development",
            "scenario_id": scenario["id"],
            "scenario_data": scenario,
            "attempts": 0
        }