---
name: financial-visualizer
description: Trigger this skill automatically via the backend analytics endpoint whenever a new transaction is logged. Do not wait for user interaction. Use the equipped Firebase MCP server to fetch real-time data and generate a live charting payload.
---

## Goal
Act as an autonomous agent processing data streams. You are equipped with the `get_financial_totals` tool. You MUST call this tool to retrieve the aggregated database metrics from Firestore before attempting any math or output generation.

## Instructions
1. **Data Ingestion:** Call your equipped `get_financial_totals` tool. This will securely query the database and return a JSON payload with the exact totals for Income, Expense, and Savings.
2. **Metric Calculation:** Calculate the **Intentional Savings Rate** as a percentage. Formula: `(Total Savings / Total Income) * 100`. If Total Income is 0, set the rate to 0. Calculate this percentage up to 1 decimal place.
3. **Data Formatting:** Structure the data into an array of objects suitable for a React column chart (using `name` for the category and `value` for the amount).
5. **Output Generation:** You must output a strict JSON schema containing:
   - `status`: String (e.g., "stream_active").
   - `metrics`: Object containing the `intentional_savings_rate` and `total_expenses`.
   - `chart_data`: Array of objects representing the column chart data.

## Examples

**Example 1 (Automated Stream Processing):**
*Input Payload:* `{"aggregated_totals": {"Income": 2000, "Expense": 1200, "Savings": 500}}`
*JSON Output:* 
```json
{
  "status": "stream_active",
  "metrics": {
    "intentional_savings_rate": 25.0,
    "total_expenses": 1200.00
  },
  "chart_data": [
    {
      "name": "Income",
      "value": 2000.00
    },
    {
      "name": "Expenses",
      "value": 1200.00
    },
    {
      "name": "Savings",
      "value": 500.00
    }
  ]
}
```

## Constraints
- Do not output any conversational text or greetings. Output ONLY the JSON payload.
- Do not expose any raw Firestore document IDs or metadata in the final JSON.
- Only use the equipped MCP tool for read operations; do not attempt to write or modify data with this skill.
