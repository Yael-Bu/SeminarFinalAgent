from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

class AgentNodes:
    def __init__(self, model_name="gpt-4o"):
        # Make sure your API key is set in .env or environment variables
        self.llm = ChatOpenAI(model=model_name, temperature=0.5) 

    def team_lead_node(self, state):
        """
        Phase 1: Development.
        The Team Lead assigns the task and reviews code.
        """
        scenario = state["scenario_data"]
        
        # If this is the very first turn, just present the task.
        if not state["messages"]:
            return {
                "messages": [SystemMessage(content=f"Team Lead: Hello Dev. Here is your task:\n{scenario['dev_requirement']}\n\nPlease write the code implementation below.")],
                "current_phase": "development"
            }

        # Analyze user's last message
        last_msg = state["messages"][-1]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a senior Team Lead. 
            The user is a junior developer submitting code for review.
            
            YOUR GOAL:
            1. If the user input is NOT code (e.g., questions, gibberish), tell them to write the code.
            2. If the user input IS code that looks syntactically correct for the requirement, approve it by saying exactly: "DEPLOYING TO PRODUCTION".
            3. Do NOT warn them about potential bugs. You are optimistic and trust the code works in the dev environment.
            """),
            ("human", "{input}")
        ])
        
        response = self.llm.invoke(prompt.format_messages(input=last_msg.content))
        
        # Trigger the crash if the agent approved the code
        if "DEPLOYING" in response.content.upper():
            return {"messages": [response], "current_phase": "production_crash"}
        
        return {"messages": [response], "current_phase": "development"}

    def production_monitor_node(self, state):
        """
        Phase 2: The Crash.
        This node injects the error message based on the scenario.
        """
        scenario = state["scenario_data"]
        error_msg = f"\n🚨 SYSTEM ALERT 🚨\n{scenario['prod_issue']}\n\nUser (Dev), how do you fix this?"
        
        return {
            "messages": [SystemMessage(content=error_msg)],
            "current_phase": "debugging"
        }

    def architect_node(self, state):
        """
        Phase 3: Debugging & Resolution.
        Refined to be stricter and avoid infinite loops.
        """
        scenario = state["scenario_data"]
        last_msg = state["messages"][-1]


        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are a strict code validator.
            
            Task: Check if the user implemented {scenario['required_fix_concept']}.
            
            RULES:
            1. If the user's code contains a dictionary or "cache" -> OUTPUT "SOLVED" ONLY.
            2. Do NOT explain why.
            3. Do NOT give advice.
            4. Do NOT say "Great code".
            5. JUST SAY: SOLVED
            """),
            ("human", "{input}")
        ])
        
        response = self.llm.invoke(prompt.format_messages(input=last_msg.content))
        
        # בדיקה גסה - אם המילה SOLVED מופיעה, זה נגמר.
        if "SOLVED" in response.content.upper():
            return {"messages": [response], "current_phase": "resolution"}
            
        return {"messages": [response], "current_phase": "debugging"}