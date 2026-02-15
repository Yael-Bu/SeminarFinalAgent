import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from production_sim import ProductionTrapSim

import sys
from datetime import datetime

class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    
    def log_only(self, message):
        if self.log and not self.log.closed:
            self.log.write(message + "\n")

    def flush(self):
        self.terminal.flush()
        if self.log and not self.log.closed:
            self.log.flush()



load_dotenv()
seen = 0  # number of messages already printed

def get_multiline_input():
    print("\n📝 You (Dev) - Type/Paste your code below.")
    print("   (Type 'DONE' on a new line and press Enter to submit)")
    print("   ---------------------------------------------------")

    lines = []

    while True:
        try:
            line = input()
        except EOFError:
            break

        if line.strip().upper() == "DONE":
            break

        lines.append(line)

    return "\n".join(lines)

# ------------------------------
# GLOBAL TRACKER FOR PRINTED MESSAGES
# ------------------------------
already_printed_ids = set()  # Stores message IDs already printed

def run_graph(app, state):
    """
    Runs the graph using stream().
    Prints only new AI messages (prevents duplicates based on id).
    """
    global already_printed_ids
    latest_state = state

    for node_state in app.stream(state):
        for node_name, node_dict in node_state.items():
            # Filter AIMessage and SYSTEMMessage
            filtered_messages = [msg for msg in node_dict.get("messages", []) if type(msg).__name__ == "AIMessage" or type(msg).__name__ == "SystemMessage"]

            # Only new messages that were not printed
            new_messages = []
            for msg in filtered_messages:
                msg_id = (
                    msg.id or 
                    msg.additional_kwargs.get("id") or 
                    msg.additional_kwargs.get("run_id") or
                    hash(msg.content) # Fallback to content hash if no ID available
                )       

                if msg_id and msg_id not in already_printed_ids:
                    new_messages.append(msg)
                    already_printed_ids.add(msg_id)

            # Print only new AI and System messages
            for msg in new_messages:
                print(f"Agent: {msg.content}")

            latest_state = node_dict

    return latest_state



def main():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"simulation_log_{timestamp}.txt"

    sys.stdout = Logger(log_filename)

    print(f"--- Production Trap Simulator Chat Mode ---")
    print(f"📝 Logging session to: {log_filename}")

    if not os.getenv("OPENAI_API_KEY"):
        print(f"❌ OPENAI_API_KEY not found.")
        return

    print("✅ API Key loaded.")
    print("Starting simulation...\n")

    student_id = input("🆔 Please enter your Student ID to begin: ").strip()
    if not student_id:
        student_id = "default_user"

    sim = ProductionTrapSim(student_id=student_id)

    app = sim.compile()

    state = sim.get_initial_state()

    # 🔥 FIRST RUN
    state = run_graph(app, state)

    while True:
        latest_state = state
        user_input = get_multiline_input()

        if isinstance(sys.stdout, Logger):
            sys.stdout.log_only(f"\n--- User Submission at {datetime.now().strftime('%H:%M:%S')} ---")
    

        if not user_input.strip():
            print("Empty input...")
            continue

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting simulation...")
            break

    
        if isinstance(sys.stdout, Logger):
            sys.stdout.log_only(user_input)
            sys.stdout.log_only("-" * 40)

        # 🔥 Instead of append — send delta state
        latest_state["messages"] = latest_state.get("messages", []) + [HumanMessage(content=user_input)]    
        state = run_graph(
            app,
            latest_state
        )

        #print(f"[DEBUG] Phase -> {state['current_phase']}")

        if state["current_phase"] == "resolution":
            print("\n" + "="*50)
            print("🏆 MISSION ACCOMPLISHED! SYSTEM STABLE.")
            print("="*50)
            sys.stdout.log.close()
            break


if __name__ == "__main__":
    main()
