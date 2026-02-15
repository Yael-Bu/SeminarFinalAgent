from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .state import SimulationState
from .agents import AgentNodes
from .scenarios import ScenarioManager

class ProductionTrapSim:
    """
    ProductionTrapSim manages the simulation of a "Production Trap" scenario.
    The simulation is implemented as a LangGraph workflow, with interruptible
    nodes, dynamic routing.

    Key Features:
    - Dynamic routing based on current_phase (development vs debugging)
    - Entry node that decides whether to start at Team Lead or Architect
    - Interruptible flow to wait for user input at key stages
    - Modular nodes: Team Lead, Production Monitor, Architect
    """

    def __init__(self, student_id: str):
        # Agent nodes contain logic for Team Lead, Architect, Production Monitor
        self.student_id = student_id
    
        self.nodes = AgentNodes()
        self.scenario_manager = ScenarioManager()

        # Initialize LangGraph workflow and memory saver
        self.workflow = StateGraph(SimulationState)
        self.memory = MemorySaver()

        # Build the simulation graph
        self._build_graph()

    def _build_graph(self):
        """
        Constructs the LangGraph workflow with professional state management.
        The workflow is designed to be interruptible and dynamically route the
        flow based on the current_phase of the simulation.
        """

        # --- 1. Add Nodes ---
        # Entry node: decides dynamically whether to go to Team Lead or Architect
        self.workflow.add_node("opening", self._opening_node)

        # Standard nodes
        self.workflow.add_node("team_lead", self.nodes.team_lead_node)
        self.workflow.add_node("production_monitor", self.nodes.production_monitor_node)
        self.workflow.add_node("architect", self.nodes.architect_node)

        # --- 2. Set Entry Point ---
        # All simulations start at the opening node
        self.workflow.set_entry_point("opening")

        # --- 3. Dynamic routing from opening node ---
        self.workflow.add_conditional_edges(
            "opening",
            self._route_from_opening,
            {
                "team_lead": "team_lead",
                "architect": "architect"
            }
        )

        # --- 4. Development Phase Routing ---
        # After Team Lead reviews code, either trigger crash or wait for user
        self.workflow.add_conditional_edges(
            "team_lead",
            self._route_after_dev,
            {
                "wait_for_user": END,
                "trigger_crash": "production_monitor"
            }
        )

        # --- 5. Production Monitor routing ---
        # Always forward to Architect after monitoring crash
        self.workflow.add_edge("production_monitor", "architect")

        # --- 6. Debugging / Resolution Routing ---
        # Architect node evaluates the fix and decides if the problem is solved
        self.workflow.add_conditional_edges(
            "architect",
            self._route_after_debug,
            {
                "wait_for_user": END,      # Fix is incomplete
                "finished": END            # Fix is correct, simulation resolved
            }
        )

    # ----------------------------
    # Node helper functions
    # ----------------------------

    def _opening_node(self, state):
        """
        Entry Node: dynamically decides whether to start with Team Lead
        or skip directly to Architect based on current_phase.
        """
        messages = state.get("messages", [])


        # Dynamic routing: if debugging, jump to Architect; else Team Lead
        if state.get("current_phase") == "debugging":
            next_node = "architect"
        else:
            next_node = "team_lead"

        # Save routing decision in state for graph edges
        return {
            "messages": messages,
            "current_phase": state.get("current_phase", "development"),
            "next_node": next_node
        }

    def _route_from_opening(self, state):
        """
        Routing function for opening node.
        Uses the `next_node` field to determine the next node.
        """
        return state.get("next_node", "team_lead")

    def _route_after_dev(self, state):
        """
        Routing function after Team Lead reviews code.
        - If code is approved (DEPLOYING), trigger production crash.
        - Otherwise, wait for user to revise code.
        """
        if state["current_phase"] == "production_crash":
            return "trigger_crash"
        return "wait_for_user"

    def _route_after_debug(self, state):
        """
        Routing function after Architect evaluates the fix.
        - If problem resolved, finish simulation.
        - Otherwise, wait for further user input.
        """
        if state["current_phase"] == "resolution":
            return "finished"
        return "wait_for_user"

    # ----------------------------
    # Graph compilation / state
    # ----------------------------

    def compile(self):
        """
        Compiles the workflow with an interrupt point.
        The simulation will pause after 'production_monitor' to wait for a fix.
        """
        return self.workflow.compile()
        

    def get_initial_state(self):
        """
        Initializes the simulation state with a random scenario.
        Returns a dictionary with:
        - messages: list of system/user messages
        - current_phase: 'development' by default
        - scenario_id: ID of the selected scenario
        - scenario_data: full scenario data
        - attempts: counter for user attempts
        """
        scenario = self.scenario_manager.get_dynamic_scenario(student_id=self.student_id)
        return {
            "messages": [],
            "current_phase": "development",
            "scenario_id": scenario["id"],
            "scenario_data": scenario,
            "attempts": 0,

            # FLAGS
             "welcome_presented": False,
            "task_presented": False,
            "crash_presented": False,
            "last_actor": None
        }

