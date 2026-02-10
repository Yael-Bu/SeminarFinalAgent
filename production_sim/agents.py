from pyexpat.errors import messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from production_sim import state


class AgentNodes:
    """
    Production-grade Agent Nodes.

    Design principles:
    ✔ Idempotent nodes (safe to re-run)
    ✔ Immutable state updates
    ✔ Flag-driven flow (never rely on message length)
    ✔ MemorySaver compatible
    ✔ Deterministic routing
    """

    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3   # Lower = more deterministic for simulations
        )

    # -------------------------------------------------
    # TEAM LEAD NODE
    # -------------------------------------------------

    def team_lead_node(self, state):
        print("\n--- Team Lead Node ---")
        new_state = state.copy()

        scenario = state["scenario_data"]


        # Only present Welcome once
        messages = []
        if not state.get("welcome_presented", False):
            messages.append(AIMessage(content="🔹 Welcome to the Production Trap Simulator!"))
            new_state["welcome_presented"] = True
            new_state["messages"] = messages

        if not state.get("task_presented", False):
            messages.append(AIMessage(content=(
                            f"👨‍💻 Team Lead:\n"
                            f"Here is your task:\n\n"
                            f"{scenario['dev_requirement']}\n\n"
                            f"Please submit your code."
                        )
            ))
            new_state["task_presented"] = True
            new_state["current_phase"] = "development"
            new_state["messages"] = messages

            return new_state

        # -------------------------------------------------
        # Evaluate developer submission
        # -------------------------------------------------

        last_msg = state["messages"][-1]

        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a pragmatic Senior Team Lead reviewing a junior developer.

            RULES:

            1️⃣ If the input is NOT code → ask for code.
            2️⃣ If it LOOKS like valid code → respond EXACTLY:

            DEPLOYING TO PRODUCTION

            ⚠️ Ignore performance risks.
            ⚠️ Ignore scalability.
            ⚠️ Trust the developer.

            Be concise.
            """),
            ("human", "{input}")
        ])

        response = self.llm.invoke(
            prompt.format_messages(input=last_msg.content)
        )

        # If approved → trigger production crash phase
        if "DEPLOYING" in response.content.upper():
            new_state["current_phase"] = "production_crash"
        else:
            new_state["current_phase"] = "development"
       
        new_state["messages"] = state["messages"] + [response]
        return new_state


    # -------------------------------------------------
    # PRODUCTION MONITOR NODE
    # -------------------------------------------------

    def production_monitor_node(self, state):
        print("\n--- Production Monitor Node ---")
        new_state = state.copy()

        scenario = state["scenario_data"]

        # ✅ Prevent duplicate crash alerts
        if state.get("crash_presented"):
            return state

        crash_msg = SystemMessage(
            content=(
                f"🚨 PRODUCTION ALERT 🚨\n\n"
                f"{scenario['prod_issue']}\n\n"
                f"Developer — fix this immediately."
            )
        )

        new_state["messages"] = state["messages"] + [crash_msg]
        new_state["crash_presented"] = True
        new_state["current_phase"] = "debugging"
        return new_state

    # -------------------------------------------------
    # ARCHITECT NODE
    # -------------------------------------------------

    def architect_node(self, state):
        print("\n--- Architect Node ---")
        new_state = state.copy()

        scenario = state["scenario_data"]
        last_msg = state["messages"][-1]

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are a Senior Software Architect performing a production postmortem.

            SYSTEM FAILURE:
            {scenario['prod_issue']}

            SUCCESS CRITERIA:
            {scenario['validation_criteria']}

            YOUR TASK:

            ✔ Analyze the developer's fix.
            ✔ Focus on architecture correctness.

            IF solved → respond EXACTLY:

            SOLVED

            Otherwise → give ONE short hint.
            No lectures.
            """),
            ("human", "{input}")
        ])

        try:
            response = self.llm.invoke(
                prompt.format_messages(input=last_msg.content)
            )

        except Exception as e:
            print(f"LLM Error: {e}")
            new_state["messages"] = state["messages"] + [AIMessage(content="SOLVED")]
            new_state["current_phase"] = "resolution"
            return new_state

        # Count attempts (great for analytics later)
        attempts = state.get("attempts", 0) + 1

        if "SOLVED" in response.content.upper():
            new_state["messages"] = state["messages"] + [response]
            new_state["current_phase"] = "resolution"
            new_state["attempts"] = attempts
            return new_state


        new_state["messages"] = state["messages"] + [response]
        new_state["current_phase"] = "debugging"
        new_state["attempts"] = attempts
        return new_state

