from pyexpat.errors import messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

from production_sim import state
import re
import json

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

        strategy = scenario['required_fix_concept']
        failure = scenario['prod_issue']
        context = scenario['dev_requirement']

        system_template = """
STRICT ROLE: You are a Senior Software Architect conducting a Technical Review. 
Your goal is to ensure code quality and system stability.

ENVIRONMENT: {context} 
OUTAGE: {failure}
HIDDEN REQUIREMENT: The fix must implement the principle of '{strategy}'.

VALIDATION RULES (Be Logical and Fair):
1. RECOGNITION: Set 'is_solved' to TRUE if the code implements the core logic of '{strategy}'.
   - POSITIVE TRIGGERS: Look for 'WAL mode', 'batch_size' (under 5000), 'time.sleep', or 'rowid' filtering.
   - If the code prevents a single long-held lock by breaking the work into small chunks with pauses, it IS a solution.
2. SCALE CHECK: If the solution is still synchronous/blocking on the entire table at once (e.g., a simple ALTER TABLE or a massive batch of 100k+), 'is_solved' must be FALSE.
3. ANALYSIS FIRST: You must briefly analyze the code logic in the 'analysis' field before deciding.

HINTING RULES (If is_solved is false):
1. FORBIDDEN WORDS: NEVER use these words in your 'hint': 'lock', 'table', 'column', 'index', 'batch', 'script', 'row', 'cache', 'token', 'header'.
2. NO SPOILERS: Do not suggest specific functions (like sleep or WAL).
3. SYSTEM OBSERVATIONS: Describe symptoms only:
   - "Telemetry shows unsustainable latency spikes under load."
   - "Health checks are failing as the service remains unresponsive."
   - "The system is struggling with resource saturation; core operations are timed out."
4. TONE: Professional and concise. Use: "The current implementation doesn't meet our stability requirements."

FORMAT REQUIREMENT:
Return ONLY a JSON object.
{{
    "analysis": "Briefly explain to yourself if the code uses non-blocking patterns (like small batches + sleep + WAL).",
    "is_solved": boolean,
    "hint": "Your cryptic symptom-based hint (empty string if solved)"
}}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", "User Code:\n\n{user_input}")
        ])

        response = self.llm.invoke(prompt.format_messages(
            failure=failure,
            strategy=strategy,
            context=context,
            user_input=last_msg.content
        ))

        content = response.content.strip()

        attempts = state.get("attempts", 0) + 1

        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)

            if json_match:
                data = json.loads(json_match.group(0))
            else:
                clean = content.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean)

            # ✅ THOUGHT ANALYSIS
            # print(f"--- Architect Thought: {data.get('analysis')} ---")

            # ✅ SOLVED
            if data.get("is_solved") is True:

                new_state["messages"] = state["messages"] + [
                    AIMessage(content="SOLVED")
                ]
                new_state["current_phase"] = "resolution"
                new_state["attempts"] = attempts
                return new_state

            # ✅ Hint
            new_state["messages"] = state["messages"] + [
                AIMessage(content=data.get("hint"))
            ]
            new_state["current_phase"] = "debugging"
            new_state["attempts"] = attempts
            return new_state

        except Exception as e:

            print(f"❌ JSON Error: {e}")

            new_state["messages"] = state["messages"] + [
                AIMessage(content="The system still shows instability under load.")
            ]
            new_state["current_phase"] = "debugging"
            new_state["attempts"] = attempts
            return new_state
