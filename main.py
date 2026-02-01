import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from production_sim import ProductionTrapSim

# טעינת משתני סביבה
load_dotenv()

def get_multiline_input():
    """
    פונקציה שמאפשרת למשתמש להקליד/להדביק קוד שלם.
    הקליטה מסתיימת רק כשהמשתמש כותב 'DONE' בשורה חדשה.
    """
    print("\n📝 You (Dev) - Type/Paste your code below.")
    print("   (Type 'DONE' on a new line and press Enter to send)")
    print("   ---------------------------------------------------")
    
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
            
        # תנאי יציאה: המשתמש כתב DONE
        if line.strip().upper() == 'DONE':
            break
        
        lines.append(line)
    
    return "\n".join(lines)

def main():
    print("--- The Production Trap Simulator v1.0 ---")
    
    # בדיקת מפתח API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # בדיקה אם המפתח קיים בקוד עצמו (למקרה ששמתם אותו שם כפתרון זמני)
        pass 
    else:
        print(f"✅ API Key loaded: {api_key[:5]}...")

    print("Starting system...")
    
    sim = ProductionTrapSim()
    app = sim.compile()
    
    # אתחול
    state = sim.get_initial_state()
    
    # קבלת המשימה הראשונה
    print("\nSystem: Initializing Scenario...")
    result = app.invoke(state)
    state = result
    print(f"\nAgent: {result['messages'][-1].content}")

    # הלולאה הראשית
    while True:
        # שימוש בפונקציה החדשה לקליטת קוד
        user_input = get_multiline_input()
        
        if not user_input.strip():
            print("Empty input, please write something...")
            continue

        if user_input.lower() in ["quit", "exit"]:
            break
            
        # הוספת ההודעה לזיכרון
        state["messages"].append(HumanMessage(content=user_input))
        
        # הרצת הסוכן
        print("\n⏳ Agent is thinking...")
        result = app.invoke(state)
        state = result
        
        # הדפסת התשובה
        agent_msg = result["messages"][-1].content
        print(f"\nAgent: {agent_msg}")
        
        if state["current_phase"] == "resolution":
            print("\n--- 🏆 Mission Accomplished! System Stable. ---")
            break

if __name__ == "__main__":
    main()