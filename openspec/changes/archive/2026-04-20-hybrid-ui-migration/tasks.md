## 1. Phase 0: Semantic Tokens Foundation

- [x] 1.1 Extract all current hex/rgba colors from `index.css` and group by purpose.
- [x] 1.2 Define semantic variable aliases (e.g., `--surface-canvas`, `--accent-primary`) in `:root` of `index.css`.
- [x] 1.3 Map these new aliases to the existing specific variables (no visual change yet).

## 2. Phase 1: Theme Plumbing

- [x] 2.1 Define `[data-theme="light"]` and `[data-theme="dark"]` blocks in `index.css` with overriding token values.
- [x] 2.2 Implement `initTheme()` logic in `frontend/src/main.jsx` (or a utility) to load theme from `localStorage` or `prefers-color-scheme`.
- [x] 2.3 Add a tiny `script` in `index.html` to set `documentElement.dataset.theme` immediately to prevent FOUT.
- [x] 2.4 Create `ThemeToggle` component in `frontend/src/components/shared/ThemeToggle.jsx`.
- [x] 2.5 Mount `ThemeToggle` in `AppLayout.jsx` or a central header.

## 3. Phase 2: Mechanical Cleanup

- [x] 3.1 Sweep `index.css` and replace all raw `#hex` and `rgba` values with semantic variables.
- [x] 3.2 Audit `h1` gradients and dropdowns for theme-hostile (fixed color) rules and wire them to variables.
- [x] 3.3 Replace hardcoded colors in React inline styles (e.g., `ProgressDashboardPage.jsx`, `AuthPage.jsx`) with CSS variables.

## 4. Phase 3: Aesthetic Pass & Polishing

- [x] 4.1 Adjust contrast and accent colors for the "ledger calm" aesthetic.
- [x] 4.2 Apply `font-variant-numeric: tabular-nums` to financial data fields (PAN, amounts).
- [x] 4.3 Refine `backdrop-filter` usage for light mode (prefer borders and paper backgrounds).
- [x] 4.4 Final verification of focus states and accessibility in both themes.
