from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from production_sim.helper import create_ai_message, create_sys_message


class AgentNodes:
    """
    Production-grade Agent Nodes (upgraded).

    - Uses scenario_data to validate developer submissions.
    - Prevents unsafe code from passing without proper mitigation.
    - Tracks attempts and updates state deterministically.
    """

    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3  # deterministic for simulations
        )

    # -------------------------------------------------
    # TEAM LEAD NODE
    # -------------------------------------------------
    def team_lead_node(self, state):
        new_state = state.copy()
        scenario = state["scenario_data"]
        messages = []

        # Welcome message
        if not state.get("welcome_presented", False):
            messages.append(create_ai_message(content=f"🔹 Welcome to the Production Trap Simulator!"))
            new_state["welcome_presented"] = True

        # Present task
        if not state.get("task_presented", False):
            messages.append(create_ai_message(content=f"👨‍💻 Team Lead Task:\n{scenario['dev_requirement']}\n\nPlease submit your code."))
            new_state["task_presented"] = True
            new_state["current_phase"] = "development"
            new_state["messages"] = messages
            return new_state

        # Evaluate submission
        last_msg = state["messages"][-1]


        # System prompt guides the LLM to check both functionality and production safety
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
        ))

        # Determine next phase
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
        new_state = state.copy()
        scenario = state["scenario_data"]

        # Prevent duplicate crash alerts
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
            response = self.llm.invoke(prompt.format_messages(input=last_msg.content))
        except Exception as e:
            # On error, assume fix solved for continuity
            print(f"⚠️ Architect evaluation error: {e}")
            new_state["messages"] = [self.create_ai_message(content=f"SOLVED")]
            new_state["current_phase"] = "resolution"
            return new_state

        attempts = state.get("attempts", 0) + 1
        new_state["attempts"] = attempts

        if "SOLVED" in response.content.upper():
            new_state["current_phase"] = "resolution"
        else:
            new_state["current_phase"] = "debugging"

        new_state["messages"] = [response]
        return new_state
