"""
Production Trap Simulator - Core Logic & Graph Orchestration
============================================================

This module defines the primary orchestration class for the simulation. 
It leverages LangGraph to create a stateful, multi-agent workflow that 
simulates a realistic transition from software development to a production crisis.

Module Responsibilities:
------------------------
1. Graph Construction: Defines the nodes and edges of the LangGraph workflow.
2. Dynamic Routing: Orchestrates the transition between different development phases 
   (development, production_crash, debugging, resolution).
3. State Initialization: Sets up the fresh SimulationState with student-specific 
   scenarios to ensure uniqueness and prevent cheating.
4. Workflow Compilation: Prepares the graph for interactive streaming and user interrupts.

Usage Example:
--------------
    # 1. Initialize the simulation with a student ID
    sim = ProductionTrapSim(student_id="123456789")
    
    # 2. Compile the graph for execution
    app = sim.compile()
    
    # 3. Obtain the initial state
    state = sim.get_initial_state()
    
    # 4. Run the simulation (interactively or via stream)
    for event in app.stream(state):
        # Process agent responses and transitions...
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .state import SimulationState
from .agents import AgentNodes
from .scenarios import ScenarioManager

class ProductionTrapSim:
    """
    ProductionTrapSim manages the simulation of a "Production Trap" scenario.
    The simulation is implemented as a LangGraph workflow with interruptible
    nodes and dynamic routing.

    Key Features:
    - Dynamic routing based on current_phase (development vs debugging).
    - Entry node that decides whether to start at Team Lead or Architect.
    - Interruptible flow to wait for user input at key stages.
    - Modular nodes: Team Lead, Production Monitor, and Architect.

    Attributes:
        student_id (str): Unique identifier used to generate personalized scenarios.
        nodes (AgentNodes): Collection of AI agent personas logic.
        scenario_manager (ScenarioManager): Logic for fetching and skinning tasks.
    """

    def __init__(self, student_id: str):
        """
        Initializes the simulation engine and graph components.
        
        Args:
            student_id (str): The ID used for deterministic scenario variations.
        """
        # Agent nodes contain logic for Team Lead, Architect, Production Monitor
        self.student_id = student_id
    
        self.nodes = AgentNodes()
        self.scenario_manager = ScenarioManager()

        # Initialize LangGraph workflow based on the SimulationState schema
        self.workflow = StateGraph(SimulationState)
        self.memory = MemorySaver()

        # Build the simulation graph structure
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

        # Standard nodes for the simulation personas
        self.workflow.add_node("team_lead", self.nodes.team_lead_node)
        self.workflow.add_node("production_monitor", self.nodes.production_monitor_node)
        self.workflow.add_node("architect", self.nodes.architect_node)

        # --- 2. Set Entry Point ---
        # All simulations start at the opening node to determine the current path
        self.workflow.set_entry_point("opening")

        # --- 3. Dynamic routing from opening node ---
        # Routes the user fresh to the Team Lead or returns them to the Architect if debugging
        self.workflow.add_conditional_edges(
            "opening",
            self._route_from_opening,
            {
                "team_lead": "team_lead",
                "architect": "architect"
            }
        )

        # --- 4. Development Phase Routing ---
        # After Team Lead reviews code, either trigger production crash or wait for user revision
        self.workflow.add_conditional_edges(
            "team_lead",
            self._route_after_dev,
            {
                "wait_for_user": END,
                "trigger_crash": "production_monitor"
            }
        )

        # --- 5. Production Monitor routing ---
        # Always forward to Architect after monitoring and reporting the crash
        self.workflow.add_edge("production_monitor", "architect")

        # --- 6. Debugging / Resolution Routing ---
        # Architect node evaluates the fix and decides if the problem is fully resolved
        self.workflow.add_conditional_edges(
            "architect",
            self._route_after_debug,
            {
                "wait_for_user": END,      # Fix is incomplete, waiting for next user iteration
                "finished": END            # Fix is correct, simulation successfully resolved
            }
        )

    # ----------------------------
    # Node helper functions
    # ----------------------------

    def _opening_node(self, state):
        """
        Entry Node: dynamically decides whether to start with Team Lead
        or skip directly to Architect based on the current_phase.
        
        Returns:
            dict: Updated state specifying the next_node for routing.
        """
        messages = state.get("messages", [])

        # Dynamic routing logic: if in debugging mode, jump to Architect; otherwise Team Lead
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
        Routing function for the opening node.
        Uses the `next_node` field to determine the target node.
        """
        return state.get("next_node", "team_lead")

    def _route_after_dev(self, state):
        """
        Routing function after Team Lead reviews code.
        - If code is approved (current_phase set to production_crash), trigger crash.
        - Otherwise, wait for the user to revise their code (End turn).
        """
        if state["current_phase"] == "production_crash":
            return "trigger_crash"
        return "wait_for_user"

    def _route_after_debug(self, state):
        """
        Routing function after Architect evaluates the fix.
        - If the problem is marked as resolution, finish the simulation.
        - Otherwise, wait for further user input (End turn).
        """
        if state["current_phase"] == "resolution":
            return "finished"
        return "wait_for_user"

    # ----------------------------
    # Graph compilation / state
    # ----------------------------

    def compile(self):
        """
        Compiles the workflow with the necessary memory and interrupt points.
        The simulation will pause for user input based on the conditional edges (END).
        
        Returns:
            CompiledGraph: A runnable LangGraph application.
        """
        return self.workflow.compile()
        

    def get_initial_state(self):
        """
        Initializes the simulation state with a unique, dynamic scenario.
        
        Fetches scenario data using the student_id to ensure a personalized 
        technical challenge and prevent copying.
        
        Returns a dictionary with:
        - messages: List of system/user messages.
        - current_phase: 'development' by default.
        - scenario_id/data: Details of the selected technical 'Trap'.
        - flags: State markers (welcome_presented, crash_presented, etc.).
        """
        scenario = self.scenario_manager.get_dynamic_scenario(student_id=self.student_id)
        return {
            "messages": [],
            "current_phase": "development",
            "scenario_id": scenario["id"],
            "scenario_data": scenario,
            "attempts": 0,

            # PROGRESS FLAGS
            "welcome_presented": False,
            "task_presented": False,
            "crash_presented": False,
            "last_actor": None
        }