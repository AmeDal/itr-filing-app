# ITR Filing App — Agentic Development Rules

## Stack
- **Backend:** FastAPI (Python) — async-only
- **Frontend:** React
- **AI Assistant:** Gemini Code Assist (Antigravity)

## Core Directives
- Read only required files via `AGENTS.md` — never scan the entire codebase
- Do not re-read files already in context
- Do not drift from established design patterns (enforced by `.agents/rules/`)
- All backend code must be async-compatible (enforced by `async-enforcement` rule)
- Keep files under ~300 lines; refactor proactively (enforced by `file-size-guard` rule)
- Update `AGENTS.md` whenever new files or folders are created
- Raise PRs against `development` branch by default (enforced by `pr-branch-policy` rule)

## Architecture Summary
- **Backend layers:** Router → Service → DAL/db.py (enforced by `separation-of-concerns` rule)
- **Frontend:** One component per page; extract sub-components for tabs/sections
- **Detailed patterns** are in `.agents/skills/` — loaded automatically when relevant

## Anti-Patterns (Quick Reference)
| Don't | Do |
|---|---|
| Sync functions in async codebase | `async def` + `await` |
| Business logic in routers | Move to `service/` |
| Growing `db.py` beyond its role | Extract to `dal/` |
| Large UI components | Break into sub-components |
