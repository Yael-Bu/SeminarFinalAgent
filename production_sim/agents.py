"""
Agent Nodes Module - Production Trap Simulator
==============================================

This module implements the specialized AI personas (Nodes) that govern 
the simulation's lifecycle. Each agent is designed with a specific 
pedagogical goal to challenge the student's technical and systemic thinking.

Key Personas:
-------------
1. Senior Team Lead:
   - Behavioral Profile: Fast-paced, results-oriented, focused on functional requirements.
   - Role: Acts as the 'Bait' by approving code that works but is not production-ready.
   - Output: Triggers the "DEPLOYING TO PRODUCTION" state.

2. Production Monitor:
   - Behavioral Profile: Deterministic system herald.
   - Role: Announces the critical failure (the 'Trap') immediately after deployment.
   - Insight: Reports symptoms (e.g., 429 Errors) but hides the root cause (e.g., missing Caching).

3. Senior Architect:
   - Behavioral Profile: High-level technical validator with a 'Strict Evaluation Scope'.
   - Role: Guides the student through the resolution phase using technical hints (Scaffolding).
   - Criteria: Enforces a specific 'Mandatory Checklist' and 'Success Criteria'.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from production_sim.helper import create_ai_message, create_sys_message


class AgentNodes:
    """
    Orchestrates the behavior of AI agents using specific LLM configurations.
    
    Attributes:
        llm (ChatOpenAI): The core language model engine, set to low temperature 
                         (0.3) for consistent and professional evaluations.
    """

    def __init__(self, model_name="gpt-4o"):
        """
        Initializes the agent nodes with the specified OpenAI model.
        
        Args:
            model_name (str): The model used for reasoning (GPT-4o recommended for code analysis).
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3  # Deterministic setting for reliable technical feedback [cite: 61]
        )

    # -------------------------------------------------
    # TEAM LEAD NODE
    # -------------------------------------------------
    def team_lead_node(self, state):
        """
        Simulates the initial development and approval phase.
        
        This node presents the task and reviews the developer's submission. 
        It purposely ignores production risks to lead the student into the 'Trap'.
        
        Args:
            state (SimulationState): The current graph state.
            
        Returns:
            dict: Updated state with phase transitions and messages.
        """
        new_state = state.copy()
        scenario = state["scenario_data"]
        messages = []

        # Welcome message logic
        if not state.get("welcome_presented", False):
            messages.append(create_ai_message(content=f"🔹 Welcome to the Production Trap Simulator!"))
            new_state["welcome_presented"] = True

        # Task Presentation: Sets the 'Bait' 
        if not state.get("task_presented", False):
            messages.append(create_ai_message(content=f"👨‍💻 Team Lead Task:\n{scenario['dev_requirement']}\n\nPlease submit your code."))
            new_state["task_presented"] = True
            new_state["current_phase"] = "development"
            new_state["messages"] = messages
            return new_state

        # Evaluation: Strict focus on functionality to allow the simulation to progress to the 'Crash' 
        last_msg = state["messages"][-1]

        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a strict Senior Team Lead reviewing code.

            OUTPUT RULES:

            ✅ If the code fully satisfies the requirement:
            Respond with EXACTLY:

            DEPLOYING TO PRODUCTION

            ❌ Otherwise:
            Give ONE short technical instruction describing what is missing.

            DO NOT:
            - Restate the requirement
            - Explain your reasoning
            - Add any extra text when approving
            """),
            ("human", "REQUIREMENT:\n{task}\n\nCODE:\n{code}")
        ])

        response = self.llm.invoke(
            prompt.format_messages(
                task=scenario["dev_requirement"],
                code=last_msg.content
            )
        )

        # Logic to trigger production_crash phase 
        if "DEPLOYING" in response.content.upper() and "WARN" not in response.content.upper():
            new_state["current_phase"] = "production_crash"
        else:
            new_state["current_phase"] = "development"

        new_state["messages"] = [create_ai_message(content=response.content)]
        return new_state

    # -------------------------------------------------
    # PRODUCTION MONITOR NODE
    # -------------------------------------------------
    def production_monitor_node(self, state):
        """
        Handles the immediate fallout of the deployment.
        
        This node reports the technical failure defined in 'prod_issue'.
        It serves as a deterministic system alert.
        
        Args:
            state (SimulationState): The current graph state.
            
        Returns:
            dict: Updated state transitioning to 'debugging' phase.
        """
        new_state = state.copy()
        scenario = state["scenario_data"]

        # Prevent duplicate crash alerts to maintain clean logging 
        if state.get("crash_presented"):
            return state

        crash_msg = create_sys_message(
            content=f"🚨 PRODUCTION ALERT 🚨\n\n{scenario['prod_issue']}\n\nDeveloper — fix this immediately."
        )
        new_state["messages"] = [crash_msg]
        new_state["crash_presented"] = True
        new_state["current_phase"] = "debugging"
        return new_state

    # -------------------------------------------------
    # ARCHITECT NODE
    # -------------------------------------------------
    def architect_node(self, state):
        """
        Evaluates the student's fix during the debugging phase.
        
        Uses a 'Strict Evaluation Scope' to verify the 'required_fix_concept'.
        Implements 'Pedagogical Scaffolding' by giving short hints rather than solutions.
        
        Args:
            state (SimulationState): The current graph state.
            
        Returns:
            dict: Updated state with attempts incremented and potential 'resolution' status.
        """
        new_state = state.copy()
        scenario = state["scenario_data"]
        last_msg = state["messages"][-1]

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are a strict technical validator. Your ONLY goal is to verify if the code satisfies the specific checklist provided below.

            STRICT EVALUATION SCOPE:
            1. Validate the code ONLY against the 'Mandatory Checklist' and 'Success Criteria'.
            2. Ignore any other best practices (security, naming conventions, documentation) unless they are in the checklist.
            3. If the user missed a specific requirement from the list, name it.
            
            MANDATORY CHECKLIST:
            {scenario.get('requirements', [])}

            SUCCESS CRITERIA:
            {scenario['validation_criteria']}

            REQUIRED ARCHITECTURAL CONCEPT:
            {scenario.get('required_fix_concept', 'N/A')}

            RESPONSE RULES:
            - If ALL items in the checklist and success criteria are met -> Respond EXACTLY with: SOLVED
            - If ANY item is missing -> Give ONE short technical hint about the missing requirement. No general advice.
            """),
            ("human", "{input}")
        ])

        try:
            # High-reasoning evaluation of the code against the checklist 
            response = self.llm.invoke(prompt.format_messages(input=last_msg.content))
        except Exception as e:
            # Graceful Failure: If LLM fails, mark as solved to prevent student blockage 
            print(f"⚠️ Architect evaluation error: {e}")
            new_state["messages"] = [create_ai_message(content=f"SOLVED")]
            new_state["current_phase"] = "resolution"
            return new_state

        # Track attempts for pedagogical assessment and potential adaptive feedback in future iterations
        attempts = state.get("attempts", 0) + 1
        new_state["attempts"] = attempts

        # Termination criteria for the Infinite Loop Prevention mechanism.
        if "SOLVED" in response.content.upper():
            new_state["current_phase"] = "resolution"
        else:
            new_state["current_phase"] = "debugging"

        new_state["messages"] = [response]
        return new_state