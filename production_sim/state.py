"""
Simulation State Module - Production Trap Simulator
===================================================

This module defines the global schema for the simulation's state management.
It utilizes LangGraph's state-sharing capabilities to maintain a consistent
memory across different AI agents and workflow nodes.

Module Responsibilities:
------------------------
1. Persistence: Defines the structure for session memory, allowing the 
   simulation to track progress across multiple user turns.
2. Deduplication Logic: Integrates with helper functions to ensure the 
   message history remains unique and concise.
3. Phase Orchestration: Stores the current stage of the simulation, enabling 
   dynamic routing between the 'Bait', 'Trap', and 'Resolution' phases.
"""

from typing import TypedDict, List, Annotated, Literal
from langchain_core.messages import BaseMessage
from production_sim.helper import add_unique_messages

class SimulationState(TypedDict):
    """
    Represents the shared memory and context of the ongoing simulation.

    This class serves as the 'Single Source of Truth' for the LangGraph 
    workflow. It tracks conversation history, scenario-specific data, 
    and pedagogical progress markers.

    Attributes:
        messages (Annotated[List[BaseMessage], add_unique_messages]): 
            A cumulative list of all messages in the session. It uses the 
            'add_unique_messages' reducer to filter duplicates and prevent 
            Context Overflow.
        
        current_phase (Literal["development", "production_crash", "debugging", "resolution"]): 
            The current stage of the pedagogical flow. Controls the dynamic 
            routing of the graph.
        
        scenario_id (str): 
            The unique identifier of the randomly selected technical scenario.
        
        scenario_data (dict): 
            The full payload of the current scenario, including the 'Bait' 
            (dev_requirement) and 'Trap' (prod_issue).
        
        attempts (int): 
            A counter tracking the number of times the student has attempted 
            to solve the production crash during the debugging phase.
        
        welcome_presented (bool): 
            A flag indicating if the initial system greeting has been displayed.
        
        task_presented (bool): 
            A flag indicating if the student has received their initial 
            development requirements from the Team Lead.
        
        crash_presented (bool): 
            A flag indicating if the 'Production Monitor' has already 
            reported the system failure.
        
        last_actor (Literal["team_lead", "architect", None]): 
            Tracks which AI persona last updated the state to assist with 
            complex routing decisions.
    """
    messages: Annotated[List[BaseMessage], add_unique_messages]
    current_phase: Literal["development", "production_crash", "debugging", "resolution"]
    scenario_id: str
    scenario_data: dict
    attempts: int
    welcome_presented: bool
    task_presented: bool
    crash_presented: bool
    last_actor: Literal["team_lead", "architect", None]