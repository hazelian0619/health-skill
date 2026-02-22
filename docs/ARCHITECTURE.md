# Architecture

```text
+---------------------------+
| API / Command Layer       |
| - /health-init            |
| - /health-query           |
| - /health-stats           |
+--------------+------------+
               |
               v
+--------------+------------+
| Decision Layer            |
| - Redline rules           |
| - LLM reasoning           |
| - Fallback                |
+--------------+------------+
               |
               v
+--------------+------------+
| Domain Layer              |
| - Rehab safety            |
| - Nutrition               |
| - TCM assessment          |
+--------------+------------+
               |
               v
+--------------+------------+
| Data Layer                |
| - Profile store           |
| - Call history            |
| - Custom rules            |
+---------------------------+
```
