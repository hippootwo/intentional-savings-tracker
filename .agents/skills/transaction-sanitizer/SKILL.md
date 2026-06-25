---
name: transaction-sanitizer
description: Trigger this skill immediately when a raw transaction payload is received to sanitize structural data, format European decimals, and enforce positive amount constraints before further processing.
---

## Goal
Sanitize and validate the incoming transaction amount to ensure it is structurally sound for database insertion and downstream cognitive validation.

## Instructions
1. Check the `amount` field in the payload.
2. If the `amount` is formatted as a string with a decimal comma (e.g., "15,50"), convert the comma to a standard period (e.g., "15.50").
3. Cast the sanitized `amount` to a standard float.
4. Verify that the resulting float is strictly greater than 0.

## Examples

**Example 1 (European Decimal Fix):**
*Input Payload:* `{"amount": "4,50", "category": "Expense", "description": "Coffee in Galway"}`
*Sanitized Output:* `{"amount": 4.5, "category": "Expense", "description": "Coffee in Galway"}`

**Example 2 (Integer to Float):**
*Input Payload:* `{"amount": "150", "category": "Income", "description": "Busking"}`
*Sanitized Output:* `{"amount": 150.0, "category": "Income", "description": "Busking"}`

## Constraints
- Fail validation immediately and return an error if the parsed amount is less than or equal to 0.
- Fail validation immediately if the amount contains non-numeric characters (other than the valid decimal comma/period).
- Do not modify the `category` or `description` fields; restrict operations strictly to the `amount`.
