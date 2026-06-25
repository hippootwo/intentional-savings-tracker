# Agentic Architecture Framework (ADK 2.0)

This document codifies the architectural principles and guidelines for building robust, scalable, and efficient AI Agent systems based on the ADK (Agent Development Kit) 2.0 framework. It serves as a blueprint for all future projects to ensure consistent, modular design and secure graph-based orchestration.

> [!CAUTION]
> **Core Developer Rule:** Never assume or take initiative when building code. Always explicitly ask for permission and await user confirmation before implementing simulated frameworks or major architectural deviations.

---

## 1. ADK 2.0 Core Philosophy

The fundamental shift in ADK 2.0 is moving away from monolithic LLM processing toward modular, graph-based orchestration and event-driven design.

- **Progressive Disclosure over Context Saturation:** Instead of loading an agent's active memory with hundreds of tools and entire codebases (causing high latency and hallucination), ADK 2.0 uses Agent Skills. These are dormant modules of expertise injected into the context window only when semantically triggered by user intent.
- **Graph-Based Orchestration:** Agents are built as stateful graph workflows. This allows complex, conditional branching where deterministic code handles simple business rules (lowering latency/cost) while LLMs handle ambiguous tasks.
- **Ambient and Event-Driven Execution:** ADK 2.0 supports "ambient agents" running autonomously in the background, listening for system events (like Pub/Sub pushes) and executing workflows independently.
- **Shift-Left Security and TDD:** Security is enforced at the point of code inception. Use Test-Driven Development (TDD), Git pre-commit hooks, local static analysis (Semgrep), and outcome-based testing to block insecure code.

---

## 2. Directory Structure & Scaffolding

The framework strongly enforces separation of concerns through a standardized layout:

```text
<project-root>/
├── app/
│   └── agent.py              # The primary agent graph and workflow definitions
├── .agents/
│   ├── CONTEXT.md            # Centralized project-specific rules and system prompts
│   ├── hooks.json            # Gating hooks for agent execution approval
│   └── skills/
│       └── <skill-name>/
│           ├── SKILL.md      # The absolute core brain of the skill
│           └── scripts/      # Optional helper scripts
├── pyproject.toml            # Dependency management
└── agents-cli-manifest.yaml  # ADK Project tracking (if applicable)
```

> [!TIP]
> Keep the core agent logic (`agent.py`) decoupled from the deployment wrappers (like FastAPI routes or Cloud Run entry points).

---

## 3. Agent Routing & Graph Workflow

ADK 2.0 abandons simple sequential prompting in favor of modeling the agent as a state machine.

- **Graph Routing:** Execution flows are defined by an edges list, chaining nodes together starting from a `START` node.
- **Pre-LLM Security Screens (Golden Rule):** To defend against prompt injection and prevent PII leaks, a **deterministic security screen node** MUST run before the LLM. If it detects a malicious payload, it short-circuits the workflow directly to human review.
- **Nodes & Context Management:** Logic is executed inside specific nodes. These nodes access the active execution state via a `Context` object and yield `Event` objects to pass data along the graph.
- **Multi-Phase Validation & Human-in-the-Loop:** For high-risk decisions (e.g., spending anomalies), the framework pauses the graph (via `RequestInput`) to enforce human-in-the-loop review before resuming.
- **Concurrency Locks:** Because graphs handle state mutation, production environments must prevent race conditions using pessimistic locking or optimistic versioning.

---

## 4. Tools vs. Skills (Brains vs. Hands)

ADK 2.0 makes a strict architectural distinction between "hands" and "brains."

- **Model Context Protocol (MCP) Servers (Tools):** The "hands." These provide stateful, persistent connections to external APIs and databases (e.g., Firebase).
- **Agent Skills (Brains):** Lightweight, ephemeral definitions that teach the agent *how* to use its tools.

### The Anatomy of `SKILL.md`

#### Part 1: YAML Frontmatter (The Trigger)
The metadata layer acts as the semantic trigger phrase used by the framework's router.
```yaml
---
name: context-validator
description: Trigger this skill when the transaction category is an Expense or Income. Use this to cross-reference the description with the category for logical consistency.
---
```

#### Part 2: Markdown Body (Persisted Prompt Engineering)
Must include:
- **Goal:** High-level objective.
- **Instructions:** Strict step-by-step logic.
- **Constraints:** "Do not" rules.
- **Examples:** Few-shot prompting mapping inputs to expected JSON outputs.

---

## 5. Integration & Infrastructure

Moving from local prototyping to production in ADK 2.0 is managed via structured event handling:

- **Agent Runtime Integration:** Deploying agents gives them a fully managed environment with built-in session management, long-term memory, secure sandboxing, and telemetry.
- **Event-Driven Messaging:** Ambient agents mount in a FastAPI app exposing endpoints like `/apps/agent_name/trigger/pubsub`. The system maps Pub/Sub subscriptions to session IDs and creates fresh workflow sessions per event.
- **Handling Failures:** Infrastructure resilience is managed via acknowledgment deadlines and routing messages to a Dead-Letter Topic (DLT) after repeated execution failures.

---

## 6. The ADK Development Lifecycle (Prototyping to Production)

> [!IMPORTANT]
> **AI INSTRUCTION: Project Initiation**
> At the start of every new project, before writing any code, the AI MUST actively ask the user to provide the **Agentic Design** details:
> 1. **The Goal:** What problem are we solving?
> 2. **The Agents:** What personas or skills are needed?
> 3. **The Graph Structure:** How does data flow between them?
> 4. **The Tools:** What external access do they need (APIs, DBs, etc)?

To ensure robust and bug-free production systems, all future projects MUST follow this 4-step ADK Development Lifecycle:

1. **Phase 1: Scaffolding & Building**
   - Initialize the `app/agent.py` and `.agents/skills` directories using the `agents-cli`.
   - Define the graph edges, deterministic gates (e.g., `PRE_LLM_SCREEN`), and generative nodes.
2. **Phase 2: Pre-Deployment Visualization (The Playground)**
   - Run the local visualizer via `agents-cli playground` (`uv run adk web app`).
   - Visually trace transaction flows to detect routing bugs, logic errors, and performance warnings (e.g., LLM context cache misses).
   - Iterate on the graph logic and prompt engineering securely and locally until 100% verified.
3. **Phase 3: Backend Deployment**
   - Once the graph behavior is completely verified in the visualizer, **freeze the agent logic**.
   - > [!IMPORTANT]
     > **Always ask for explicit user permission before deploying the backend.**
   - Deploy the ADK environment directly to a production runtime (like Google Cloud Run). The verified graph becomes the secure backend API service.
4. **Phase 4: Frontend Integration**
   - Build custom frontends (Web, iOS, Android) that act purely as "dumb clients." 
   - The frontend handles UI/UX and simply sends raw payloads to the deployed backend API, trusting the ADK graph to handle all intelligence and routing.

> [!WARNING]
> **API Key Management:** API keys will be set and will probably be different for every project. Ensure you use the correct `.env` configuration per environment. Additionally, beware of system-level conflicts (e.g., `google.genai` SDK prioritizing `GOOGLE_API_KEY` over `GEMINI_API_KEY`), and always explicitly handle key loading to prevent silent authentication failures.
