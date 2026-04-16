---
description: Enforces async-first patterns in all backend Python files. All functions must use async def, all I/O must use await, no sync HTTP clients or DB drivers.
alwaysApply: false
globs: ["backend/**/*.py"]
---

# Async Enforcement Rule

## Mandatory Patterns

1. **All function definitions** must use `async def`, not `def`
2. **All I/O operations** must use `await` — never call blocking I/O directly
3. **No `time.sleep()`** — use `asyncio.sleep()` instead
4. **No synchronous HTTP clients** — use `httpx.AsyncClient`, not `requests`
5. **No synchronous DB drivers** — use async-compatible drivers (e.g., `asyncpg`, `aiosqlite`, `motor`)

## Validation Checklist

Before writing any backend function, verify:
- [ ] Uses `async def`
- [ ] All DB calls use `await`
- [ ] All HTTP calls use `await`
- [ ] No blocking `sleep` or `time.sleep`
- [ ] No `requests.get/post` — use `httpx` async instead
