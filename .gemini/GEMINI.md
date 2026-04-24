# ITR Filing App — Agentic Development Rules

## Stack
- **Backend:** FastAPI (Python) — async-first, PyMongo `AsyncMongoClient`
- **Frontend:** React + Vite
- **AI Assistant:** Gemini Code Assist (Antigravity)
- **Integration branch:** Treat `development` as the default branch for PRs and merge targets, even if the GitHub remote default/HEAD points elsewhere

## Core Directives
- Read only required files via `AGENTS.md` — never scan the entire codebase
- Do not re-read files already in context
- Do not drift from established design patterns
- All backend code must be async-compatible
- Keep files under ~300 lines; refactor proactively when a touched file crosses the soft limit
- Update `AGENTS.md` whenever new files or folders are created
- Raise PRs against `development` branch by default unless the user explicitly asks for a different base

## Architecture Summary
- **Backend layers:** Router → Service → DAL/db.py (see `.agents/rules/separation-of-concerns.md` when changing backend structure)
- **Frontend:** One component per page; extract sub-components for tabs/sections
- **Detailed patterns** live in `.agents/skills/`; open only the relevant skill file when the task needs it

## Progressive Loading
- Start each session with only this file and `AGENTS.md`
- Use `AGENTS.md` as the navigation map, then open the smallest relevant code, doc, or spec file
- For backend FastAPI/database/auth/service work, open `.agents/skills/fastapi-backend/SKILL.md`
- For frontend React/page/routing/API-integration work, open `.agents/skills/react-frontend/SKILL.md`
- For OpenSpec work, open the matching `.agents/skills/openspec-*/SKILL.md` skill or the mirrored `.gemini/skills/openspec-*/SKILL.md`
- Do not preload all skills, workflows, docs, or archived OpenSpec changes; read archive files only when historical rationale is directly relevant

## Anti-Patterns (Quick Reference)
| Don't | Do |
|---|---|
| Sync functions in async codebase | `async def` + `await` |
| Business logic in routers | Move to `services/` |
| Growing `db.py` beyond its role | Extract to `dal/` |
| Large UI components | Break into sub-components |
