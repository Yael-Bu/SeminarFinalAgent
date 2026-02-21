"""
Production Trap Simulator - CLI Orchestrator
===========================================

This module serves as the primary entry point and user interface for the 
'Production Trap' simulation. It bridges the gap between the LangGraph 
backend and the student via a Command Line Interface (CLI).

Core Responsibilities:
----------------------
1. Session Management: Initializes the simulation state based on the Student ID 
   to ensure a personalized and anti-cheat protected environment.
2. Forensic Logging: Implements a dual-stream Logger that captures the entire 
   pedagogical process, including student code submissions and AI agent 'thoughts'.
3. Real-time Execution: Manages the iterative loop of the LangGraph workflow, 
   handling the transition from the 'Bait' phase (development) to the 
   'Trap' phase (production crash) and finally the 'Resolution'.
4. Input Handling: Provides a robust multiline input mechanism tailored for 
   pasting and submitting complex code blocks.
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from production_sim import ProductionTrapSim

import sys
from datetime import datetime

class Logger:
    """
    A custom logging class that redirects standard output to both the terminal 
    and a persistent log file.
    """
    def __init__(self, filename):
        """
        Initializes the Logger with a target filename for disk storage.
        """
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        """
        Writes a message simultaneously to the console and the log file.
        """
        self.terminal.write(message)
        self.log.write(message)
    
    def log_only(self, message):
        """
        Writes a message only to the log file. Used for capturing internal 
        data or user code without cluttering the user's terminal.
        """
        if self.log and not self.log.closed:
            self.log.write(message + "\n")

    def flush(self):
        """
        Ensures all buffered output is physically written to the terminal and file.
        """
        self.terminal.flush()
        if self.log and not self.log.closed:
            self.log.flush()

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()
seen = 0  # Global tracker for message counts

def get_multiline_input():
    """
    Captures multi-line text input from the terminal until the user types 'DONE'.
    This allows students to paste formatted code blocks easily.
    
    Returns:
        str: The concatenated string of all lines entered.
    """
    print("\n📝 You (Dev) - Type/Paste your code below.")
    print("   (Type 'DONE' on a new line and press Enter to submit)")
    print("   ---------------------------------------------------")

    lines = []

    while True:
        try:
            line = input()
        except EOFError:
            break

        # Check for the submission keyword 'DONE'
        if line.strip().upper() == "DONE":
            break

        lines.append(line)

    return "\n".join(lines)

# ------------------------------
# GLOBAL TRACKER FOR PRINTED MESSAGES
# ------------------------------
already_printed_ids = set()  # Stores unique message IDs to prevent duplicate output

def run_graph(app, state):
    """
    Executes the simulation graph using a streaming approach. 
    It iterates through node updates and prints only new AI or System responses.
    
    Args:
        app: The compiled LangGraph workflow.
        state (dict): The current simulation state.
        
    Returns:
        dict: The final updated state after the graph execution segment.
    """
    global already_printed_ids
    latest_state = state

    # Stream the graph execution to capture per-node changes
    for node_state in app.stream(state):
        for node_name, node_dict in node_state.items():
            # Filter messages to only process AI and System feedback
            filtered_messages = [
                msg for msg in node_dict.get("messages", []) 
                if type(msg).__name__ in ["AIMessage", "SystemMessage"]
            ]

            # Identify new messages that haven't been displayed to the user yet
            new_messages = []
            for msg in filtered_messages:
                # Attempt to find a unique ID; fallback to content hash for stability
                msg_id = (
                    msg.id or 
                    msg.additional_kwargs.get("id") or 
                    msg.additional_kwargs.get("run_id") or
                    hash(msg.content)
                )       

                if msg_id and msg_id not in already_printed_ids:
                    new_messages.append(msg)
                    already_printed_ids.add(msg_id)

            # Print the filtered responses to the terminal
            for msg in new_messages:
                print(f"Agent: {msg.content}")

            # Keep track of the most recent state returned by the nodes
            latest_state = node_dict

    return latest_state


def main():
    """
    Main entry point for the Production Trap Simulator. 
    Handles initialization, the primary chat loop, and session logging.
    """

    # ---------------------------------------------------------
    # LOGGING DIRECTORY SETUP
    # ---------------------------------------------------------
    
    # Define the target directory for session logs
    results_dir = "Results"
    
    # Ensure the 'Results' directory exists to prevent FileNotFoundError
    # This maintains the forensic integrity of the simulation logs [cite: 133, 192]
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        
    # Generate a unique filename with a timestamp within the Results folder
    # This creates a 'black box' record of the student's learning process 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(results_dir, f"simulation_log_{timestamp}.txt")

    # ---------------------------------------------------------
    # SYSTEM INITIALIZATION
    # ---------------------------------------------------------

    # Redirect standard output (stdout) to the custom dual-stream Logger
    sys.stdout = Logger(log_filename)

    print(f"--- Production Trap Simulator Chat Mode ---")
    print(f"📝 Logging session to: {log_filename}")

    # Security check: Ensure the API key is present before proceeding
    if not os.getenv("OPENAI_API_KEY"):
        print(f"❌ OPENAI_API_KEY not found.")
        return

    print("✅ API Key loaded.")
    print("Starting simulation...\n")

    # Identification phase for anti-cheat and scenario generation
    student_id = input("🆔 Please enter your Student ID to begin: ").strip()
    if not student_id:
        student_id = "default_user"

    # Initialize the simulation core and generate a unique scenario
    sim = ProductionTrapSim(student_id=student_id)
    app = sim.compile()
    state = sim.get_initial_state()

    # FIRST RUN: Initiates the simulation and presents the starting task (The 'Bait')
    state = run_graph(app, state)

    # Core interaction loop
    while True:
        latest_state = state
        user_input = get_multiline_input()

        # Log user activity internally for grading or audit purposes
        if isinstance(sys.stdout, Logger):
            sys.stdout.log_only(f"\n--- User Submission at {datetime.now().strftime('%H:%M:%S')} ---")
    
        # Handle empty submissions
        if not user_input.strip():
            print("Empty input...")
            continue

        # Exit commands
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting simulation...")
            break

        # Log the actual code/text submitted by the student
        if isinstance(sys.stdout, Logger):
            sys.stdout.log_only(user_input)
            sys.stdout.log_only("-" * 40)

        # Append the new user message to the state and re-run the graph
        latest_state["messages"] = latest_state.get("messages", []) + [HumanMessage(content=user_input)]    
        state = run_graph(app, latest_state)

        # Check if the simulation has reached the success state
        if state["current_phase"] == "resolution":
            print("\n" + "="*50)
            print("🏆 MISSION ACCOMPLISHED! SYSTEM STABLE.")
            print("="*50)
            sys.stdout.log.close()
            break


if __name__ == "__main__":
    main()