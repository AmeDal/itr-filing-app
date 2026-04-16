---
description: Pre-push quality checklist to run before every git push.
---

# Pre-Push Checklist

Run this workflow before every `git push` to ensure code quality.

---

## Step 1: Python Linting & Formatting

Run the following commands and share the output:

1. `cd backend && python -m ruff check .` — Lint all Python files
2. `cd backend && python -m ruff format --check .` — Check formatting

Fix any issues before proceeding.

---

## Step 2: Type Checking

1. `cd backend && python -m mypy . --ignore-missing-imports` — Type check all Python files

Fix any type errors before proceeding.

---

## Step 3: Backend Tests

1. `cd backend && python -m pytest -v` — Run all backend tests

All tests must pass.

---

## Step 4: Frontend Lint & Build

1. `cd frontend && npm run lint` — Lint all frontend files
2. `cd frontend && npm run build` — Ensure production build succeeds

Fix any issues before proceeding.

---

## Step 5: Verify AGENTS.md

1. Review `AGENTS.md` — ensure it reflects the current file structure
2. If any new files/folders were created since the last push, add them

---

## Step 6: Refactoring Check

1. Scan all files for any exceeding ~300 lines
2. If found, flag them and refactor before pushing

---

## Step 7: Run Python Refactor Workflow

Trigger `/python-refactor` to clean up:
- Unused imports
- Agent-generated comments
- Whitespace and spacing
- Secrets in code

---

## Final Checklist

- [ ] Python linting passes
- [ ] Type checking passes
- [ ] Backend tests pass
- [ ] Frontend linting passes
- [ ] Frontend builds successfully
- [ ] `AGENTS.md` is up to date
- [ ] No files exceed ~300 lines
- [ ] Python refactor workflow completed
