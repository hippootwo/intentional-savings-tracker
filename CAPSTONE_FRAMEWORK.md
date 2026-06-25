# Intentional Spending Tracker: Capstone Architecture & Framework (ADK 2.0)

## 1. Executive Summary
The **Intentional Spending Tracker** is a modern, full-stack application designed to transform passive expense tracking into a deliberate, conscious process. This project answers the prompt of the **AI Agents: Intensive Vibe Coding Capstone Project** by utilizing the **ADK 2.0 framework** to enforce *intentionality* in everyday financial behavior. It prevents impulse logging through psychological "speed bumps", pre-LLM security screens, and stateful graph-based cognitive validation.

---

## 2. Framework Overview (ADK 2.0 Integration)
The project implements an ADK 2.0 decoupled architecture, positioning the AI as a graph-based state machine rather than a simple middleware chatbot.

*   **Frontend (React + Vite):** A responsive, premium UI capturing user input and requiring deliberate confirmation before sending payloads.
*   **Agent Graph (app/agent.py):** The core intelligence layer. It receives payloads, runs a Deterministic Pre-LLM Security Screen, and routes data through stateful graph nodes to specialized LLM-driven "Skills" to evaluate context.
*   **Database (Firebase Firestore):** A NoSQL cloud database where approved transaction data is securely stored.
*   **Resilient Fallback & Event Handling:** To ensure reliability against API failures, the graph employs deterministic fallbacks. Ambient execution supports Pub/Sub integration for background analytics processing.

---

## 3. Scaffolding & Agent SKILLS Creation
Instead of relying on a monolithic prompt, the agent utilizes Progressive Disclosure via dynamic skill routing.

### Skill Scaffolding
Skills are stored under `.agents/skills/`. The ADK framework also relies on `.agents/CONTEXT.md` for global rules and `.agents/hooks.json` for security gating.
The primary graph logic resides in `app/agent.py`.

### Core Agent Skills
*   **`transaction-sanitizer`**: Pre-LLM security screen. Cleanses payloads deterministically to prevent injection or malformed data before LLM processing.
*   **`context-validator`**: Cross-references the transaction's description with its category for logical consistency. Can pause the graph (via `RequestInput`) for human-in-the-loop review.
*   **`stoic-reinforcer`**: Routed when a user logs "Savings". Provides positive, Stoic-inspired reinforcement.
*   **`financial-visualizer`**: Equipped with MCP tools to query live Firestore data and autonomously generate charting payloads for the analytics dashboard.

---

## 4. Capstone Project Integration
This architecture satisfies the core requirements of the Vibe Coding Agents Capstone through the lens of ADK 2.0:

*   **Solves a Real-World Problem:** Promotes financial mindfulness.
*   **Agentic Workflows:** The AI validates, rejects, or warns users via a Graph-Based Workflow with explicit human-in-the-loop pause nodes.
*   **Tool Usage:** Uses Model Context Protocol (MCP) servers (the "Hands") decoupled from the Agent Skills (the "Brains").
*   **Modular Architecture:** The ADK 2.0 folder structure (`app/agent.py`, `.agents/skills/`) makes the agent highly extensible and ready for Agent Runtime deployment.

---

## 5. Firebase MCP Integration & Tooling
The project successfully utilizes an MCP server configured for Firebase.
*   **Seamless Database Integration**: The MCP server securely bridges the gap between the agent graph and Firebase, allowing deterministic tools to query and mutate Firestore data.
*   **Tool Execution**: Skills like `financial-visualizer` utilize equipped MCP tools to provide real-time analytical capabilities without monolithic system prompts.

---

## 6. Scalability Opportunities
*   **Event-Driven Messaging:** Using Pub/Sub, the system can trigger background analytics or anomaly detection agents without blocking the main UI thread.
*   **Concurrency Locking:** Implementing pessimistic locking in the graph to ensure multi-threaded requests do not double-execute transactions.
*   **Shift-Left Security:** Utilizing Semgrep and Git pre-commit hooks to ensure agent instructions remain secure before production deployment.

---

## 7. Potential Weaknesses and Improvements

### Current Weaknesses
*   **Increased Latency:** LLM-driven nodes introduce network latency compared to direct database writes.
*   **Prompt Brittleness:** Edge cases could cause the LLM to misinterpret context, despite the pre-LLM security screens.

### Areas for Improvement
*   **Optimized Streaming:** Implementing server-sent events (SSE) mapped directly from the graph `Event` yields.
*   **LLM Model Fine-Tuning:** Transitioning to a fine-tuned, smaller model for core validation tasks.

---

## 8. Architectural Node Graph (ADK 2.0 State Machine)

```mermaid
graph TD
    User([User]) -->|Inputs Transaction| UI[React Frontend]
    UI -->|POST /api/validate-transaction| API[FastAPI / PubSub Endpoint]
    
    subgraph ADK 2.0 Workflow Graph (app/agent.py)
        API -->|START Node| PreScreen[Pre-LLM Security Screen Node]
        PreScreen -->|Pass| Router{State Machine Router}
        PreScreen -->|Fail/Malicious| Human[RequestInput: Human-in-the-Loop]
        
        Router -->|If Savings| Stoic[Skill Node: stoic-reinforcer]
        Router -->|If General Expense| Context[Skill Node: context-validator]
        Router -->|If Analytics Event| Viz[Skill Node: financial-visualizer]
        
        Stoic -.-> Gemini[Gemini 3.1 Flash Lite]
        Context -.-> Gemini
        Viz -.-> Gemini
        
        Gemini -.->|Executes Tools| MCP[(Firebase MCP Tools)]
    end
    
    Human -->|Manual Override| DB
    Gemini -->|JSON Output/Event Yield| API
    API -->|Approved| DB[(Firebase Firestore)]
    API -->|Response/Warning| UI
```
