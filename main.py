import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from production_sim import ProductionTrapSim

load_dotenv()


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

def run_graph(app, state):
    """
    Runs the graph using stream().
    Correctly handles node-scoped events and only prints new messages.
    """
    latest_state = state
    seen = 0  # number of messages already printed

    for node_state in app.stream(state):
        for node_name, node_dict in node_state.items():
            new_messages = node_dict.get("messages", [])[seen:]
            for msg in new_messages:
                print(f"Agent: {msg.content}")
            
            # update the count of messages seen
            seen = len(node_dict.get("messages", []))
            latest_state = node_dict

    return latest_state


def main():

    print("--- Production Trap Simulator Chat Mode ---")

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found.")
        return

    print("✅ API Key loaded.")
    print("Starting simulation...\n")

    sim = ProductionTrapSim()
    app = sim.compile()

    state = sim.get_initial_state()

    # 🔥 FIRST RUN
    state = run_graph(app, state)

    while True:
        latest_state = state
        user_input = get_multiline_input()

        if not user_input.strip():
            print("Empty input...")
            continue

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting simulation...")
            break

        # 🔥 Instead of append — send delta state
        latest_state["messages"] = latest_state.get("messages", []) + [HumanMessage(content=user_input)]    
        state = run_graph(
            app,
            latest_state
        )

        print(f"[DEBUG] Phase -> {state['current_phase']}")

        if state["current_phase"] == "resolution":
            print("\n" + "="*50)
            print("🏆 MISSION ACCOMPLISHED! SYSTEM STABLE.")
            print("="*50)
            break


if __name__ == "__main__":
    main()
