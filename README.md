# 🚀 Production Trap Simulator

**Project:** Agent-Based Simulator for Real-World Industry Scenarios

## 📋 Overview
[cite_start]The **Production Trap Simulator** is an interactive, agentic workflow designed to bridge the gap between academic coding and the high-pressure realities of software production[cite: 8]. [cite_start]Unlike standard coding exercises, this system acts as a "problem generator," placing the student in a realistic lifecycle of a production failure[cite: 15, 16]. [cite_start]The simulation forces users to navigate ambiguous requirements, professional friction, and critical system outages that generic AI tools struggle to solve in a single step[cite: 26, 96].

---

## 🤖 Multi-Agent Architecture
The system is built using **LangGraph** to manage a stateful, cyclic workflow involving distinct professional personas:

* **Senior Team Lead Node**: Focuses on functional requirements. This agent simulates the common industry pitfall of approving code that "works" but isn't "production-ready," eventually triggering a deployment to production.
* **Production Monitor Node**: Acts as the automated alerting system. It detects critical failures—such as database locks or API rate limits—and reports them as high-priority incidents.
* **Software Architect Node**: Conducts the post-mortem analysis. This agent is strict and requires the student to implement specific architectural patterns (e.g., non-blocking DDL, caching) before the task is marked as "Solved".

---

## 🧠 Strategic Design: AI-Resistance & Scalability
[cite_start]To satisfy the pedagogical goals of the assignment, the simulator implements several "AI-Resistant" strategies[cite: 94]:

* [cite_start]**Dynamic Scenario Mutation (Scale)**: The `ScenarioManager` leverages a generative model to mutate base scenarios[cite: 102]. [cite_start]By varying table names, variable identifiers, and tech-stack specifics for every run, the system ensures that 60+ students cannot simply share solutions[cite: 101, 105].
* [cite_start]**Human-in-the-Loop Pressure**: The agents are designed to simulate interpersonal dynamics, such as a "nitpicking" reviewer or a stressed manager, forcing students to justify their technical decisions under pressure[cite: 106, 107].
* [cite_start]**Contextual Dependency**: Success requires understanding the unique "incident report" generated during the `production_crash` phase[cite: 85, 99]. [cite_start]A simple copy-paste into an LLM often fails because the "bug" is only visible through the simulator's specific production logs[cite: 100].

---

## 🛠 Technical Stack
* **Core Logic**: Python 3.10+.
* **Orchestration**: `LangGraph` for stateful transitions and interruptible flows.
* **Memory Management**: `TypedDict` and `MemorySaver` to track attempts and message history across phases.
* **Models**: Integration with GPT-4o for deterministic yet adaptive agent responses.

---

## 🎮 How to Run
1.  **Environment**: Ensure you have your `OPENAI_API_KEY` in a `.env` file.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Execute**:
    ```bash
    python main.py
    ```

---

## 🎯 Educational Objectives
* [cite_start]**Beyond Syntax**: Teaches students to think about system stability and production risks, not just logic[cite: 26].
* [cite_start]**Incident Response**: Provides a safe environment to practice debugging "Ghost-in-the-machine" bugs[cite: 82, 83].
* [cite_start]**Professional Communication**: Simulates the nuances of code reviews and technical justification in a corporate environment[cite: 76, 77].

---

[cite_start]**"Bridging the gap between the classroom and the industry through agentic simulation."** [cite: 8]