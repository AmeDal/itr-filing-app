## Context

The current application is locked into a dark-theme visual style with many styling rules hardcoded in `index.css` or applied via inline React styles. This prevents theme flexibility and complicates global UI updates.

## Goals / Non-Goals

**Goals:**
- Centralize all themeable properties into semantic CSS variables.
- Support both light and dark modes with a single "hybrid" visual language.
- Persist user theme choice and respect system preferences.
- Eliminate hardcoded color values and theme-hostile CSS rules.

**Non-Goals:**
- Creating a clone of another product's UI (e.g., Linear, Vercel, Stripe).
- Moving the entire styling system to a new framework (e.g., Tailwind, Shadcn).
- Refactoring the entire component structure (focus is on styles).

## Decisions

### 1. Theming Mechanism: CSS Data Attributes
- **Choice**: Use `[data-theme="light|dark"]` on the `html` or `body` element.
- **Rationale**: Cleanest way to toggle themes without re-rendering the entire React tree. Allows CSS variables to be redefined in scope correctly.
- **Alternatives**: Global React State/Context (higher re-render overhead) or Multiple Stylesheets (harder to manage).

### 2. Token Architecture: Semantic Layering
- **Choice**: Define primitive colors (gray-10, indigo-50) but only expose semantic aliases (surface-canvas, text-primary) to components.
- **Rationale**: Allows changing the "feel" of a theme (e.g., making the background slightly warmer) by updating one variable without touching every component.

### 3. Visual Aesthetic: Ledger Calm
- **Choice**: Minimalist, high contrast (but soft), responsive to financial context.
- **Rationale**: Tax applications should feel serious and trustworthy. Tabular numbers for scanned IDs/amounts improve legibility.

## Risks / Trade-offs

- **[Risk] Flash of Unstyled Theme (FOUT)**: User sees dark mode for a split second before JS loads light mode.
  - **Mitigation**: Place a tiny blocking `script` in `index.html` to set the theme before the React app boots.
- **[Risk] High-Contrast Issues in Light Mode**: Glass effects can look "dirty" or unreadable in light mode.
  - **Mitigation**: Prefer solid surfaces and subtle borders (`--border-subtle`) in light mode over heavy blur.
- **[Risk] Inline Styles**: Hardcoded `style={{ color: '#fff' }}` in JSX will override CSS variables.
  - **Mitigation**: Systematic manual sweep during Phase 2 cleanup.
