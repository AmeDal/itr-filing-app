---
description: Flags files exceeding ~300 lines for refactoring before adding new code. Proposes split patterns for both backend and frontend files.
alwaysApply: false
globs: ["backend/**/*.py", "frontend/src/**/*.jsx", "frontend/src/**/*.js"]
---

# File Size Guard Rule

## Threshold
- **~300 lines** is the soft limit for any single file

## When a File Exceeds 300 Lines

1. **STOP** — do not add more code to it
2. **Flag it** — notify the user that the file needs refactoring
3. **Propose a split:**

| File growing too large | Extract to... |
|---|---|
| `db.py` | `dal/*_dal.py` per domain |
| `schema.py` | `schemas/*_schema.py` per domain |
| A single service file | Multiple service files by sub-task |
| `utils.py` | Domain-specific utility modules |
| Page component with tabs | One sub-component per tab in `components/<page>/` |
| Page with complex forms | One sub-component per section |

4. Update `AGENTS.md` after any split
