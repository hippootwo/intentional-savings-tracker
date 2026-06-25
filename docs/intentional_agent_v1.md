# Intentional Agent (v 1.0)
**Core Middleware & AI Validation Pipeline**

The `intentional_agent` is the intelligent backend gateway of the Intentional Spending Tracker. Built on FastAPI, it serves as the absolute gatekeeper between the user's React dashboard and the Firestore database. Its primary objective is to introduce "positive friction" into the user's financial habits by forcing them to justify their spending through a two-phase hybrid validation pipeline.

---

## 1. System Architecture

The agent is designed as a strict, non-bypassable middleware. All transaction requests from the frontend must pass through this pipeline.

* **Framework:** FastAPI
* **Deterministic Layer:** Pydantic
* **Cognitive Layer:** Google Generative AI (`gemini-3.5-flash`)
* **Persistence Layer:** Firebase Admin SDK (Firestore)

---

## 2. The Two-Phase Hybrid Pipeline

### Phase 1: Deterministic Validation (The Bouncer)
Before the AI ever sees the data, the payload must pass strict mathematical and structural rules enforced by Pydantic.

**Skills & Rules:**
* **European Sanitization:** Automatically detects and converts comma decimals (e.g., `15,50`) into strict float notations (`15.50`).
* **Positive Number Guard:** Instantly rejects any negative inputs (`amount <= 0`) with a strict `400 Bad Request`.
* **Heuristic Flagging System:** Scans the data and invisibly appends context flags for the LLM:
  * `missing_context`: Triggered if the description field is left completely blank.
  * `suspiciously_low`: Triggered if the amount is `< $2.00`.
  * `high_impact`: Triggered if the amount is `> $150.00`.

### Phase 2: Cognitive Validation (The Financial Advisor)
If the payload passes Phase 1, the sanitized data and heuristic flags are packaged into a JSON payload and handed off to the Gemini LLM for cognitive processing.

**Skills & Rules:**
* **Contextual Mismatch Detection:** The AI cross-references the `description` with the `category`. If the description implies an expense (e.g., "Coffee in Galway") but the category is labeled "Income", it will flag the transaction and return a warning.
* **Mandatory Description Guard:** If Phase 1 triggered BOTH the `high_impact` and `missing_context` flags, the AI will issue a strict `rejected` status, forcing the user to explain the large purchase.
* **Savings Reinforcement:** If the category is strictly "Savings", the AI abandons its strict persona and provides a complimentary, encouraging message to reinforce positive financial behavior.

---

## 3. Graceful Degradation & Resilience

The agent is designed for 100% uptime from the user's perspective, even if the underlying LLM fails.

* **The Offline Fallback:** If the Gemini API experiences a timeout, rate limit (`429 Quota Exceeded`), or crashes, the agent catches the exception. Instead of returning a `500 Server Error`, it gracefully returns a fallback payload:
  `{"status": "warning", "user_message": "Sorry, validation offline. Please review and confirm your transaction manually."}`
* This triggers the frontend's confirmation modal, allowing the user to proceed without being permanently blocked by an API outage.

---

## 4. Authoritative Database Writes

The FastAPI backend is the sole entity authorized to write to Firestore via the Firebase Admin SDK.

* **Approved Transactions:** If the AI returns an `approved` status, the agent automatically time-stamps the payload and writes it to the `transactions` collection with the metadata flag: `"ai_overridden": false`.
* **The Override Endpoint (`/api/force-submit`):** If the AI returns a `warning` or `rejected` status, the frontend presents a "Confirm Anyway" modal. If the user overrides the AI, this secondary endpoint receives the payload. It bypasses Phase 2 and writes directly to Firestore, but permanently tags the document with `"ai_overridden": true` for future behavioral analytics.
