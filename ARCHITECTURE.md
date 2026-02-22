# Health Agent Skill Architecture

## 4-Layer Architecture

+-----------------------------+
| API Layer                   |
| - OpenClaw SDK endpoints    |
| - Input validation          |
+--------------+--------------+
               |
               v
+--------------+--------------+
| Decision Layer              |
| - Rules-first routing       |
| - HITL escalation policy    |
| - Risk scoring              |
+--------------+--------------+
               |
               v
+--------------+--------------+
| Domain Layer                |
| - user_profile_init         |
| - tcm_diagnosis             |
| - nutrition_assess          |
| - rehab_safety_check        |
+--------------+--------------+
               |
               v
+--------------+--------------+
| Data Layer                  |
| - profile_schema.json       |
| - local policy tables       |
| - audit logs (optional)     |
+-----------------------------+

## Data Flow (User Query)

1) User request arrives at API Layer.
2) Input is validated against JSON Schema.
3) Decision Layer applies rules and risk checks.
4) Decision Layer invokes Domain capability modules.
5) Domain outputs are merged into personalized_advice.
6) Output is filtered by safety and disclaimers.

## Safety Mechanisms (3 Layers)

1) Input Layer
   - Schema validation
   - Red-flag keyword detection
   - Reject empty/unsafe inputs

2) Decision Layer
   - Rules-first, avoid unnecessary LLM use
   - Risk scoring with thresholds
   - need_hitl flag when high risk or ambiguous

3) Output Layer
   - Safety template and disclaimers
   - Remove prescriptive medical claims
   - Provide escalation guidance when need_hitl=true

## Extensibility (New Domain Expert)

To add a new Domain Expert:
1) Define new capability with Input/Output JSON Schema.
2) Add routing rule in Decision Layer.
3) Register module in the Domain Layer registry.
4) Update personalized_advice to include component output.
5) Add tests for schema validation and safety flags.
