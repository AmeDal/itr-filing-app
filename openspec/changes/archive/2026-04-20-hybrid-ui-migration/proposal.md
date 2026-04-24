## Why

Currently, the ITR Filing App uses a hardcoded dark-only theme defined in `index.css` with many inline styles and direct color values. This makes the UI difficult to maintain, inconsistent in some areas, and restricts accessibility by not supporting light mode or system preferences. Centralizing our visual language into semantic tokens and implementing a hybrid minimalist theme will improve readability, maintainability, and user experience while providing a professional, ledger-like aesthetic suitable for a tax product.

## What Changes

- **Semantic CSS Tokens**: Introduction of a comprehensive set of semantic CSS variables (e.g., `--surface-canvas`, `--text-primary`) to replace hardcoded colors and existing specific variables.
- **Theme Plumbing**: Implementation of `data-theme="light"` and `data-theme="dark"` on the document level, with logic to handle `localStorage` persistence and `prefers-color-scheme` system settings.
- **Theme Toggle UI**: A new `ThemeToggle` component to allow users to switch themes manually.
- **Style Cleanup**: A systemic sweep to replace hardcoded hex/rgba values and "theme-hostile" rules with semantic variables.
- **Aesthetic Refinement**: Shift towards a "ledger calm" direction with restrained color use, refined typography hierarchy (including tabular numbers for financial data), and purposeful motion.

## Capabilities

### New Capabilities
- `theme-management`: Implementation of the theme switching logic, persistence, and system preference detection.
- `ui-theme-control`: User interface component for initiating theme changes.

### Modified Capabilities
- `document-upload`: UI refinement for the upload workflow to support dual themes.
- `filing-dashboard`: UI refinement for progress tracking and summary views to support dual themes.

## Impact

- `frontend/src/index.css`: Majority of the visual changes and token definitions.
- `frontend/src/App.jsx` / `frontend/src/main.jsx`: Initialization and layout injection.
- `frontend/src/components/shared/`: New `ThemeToggle` component.
- All frontend pages: Migration from hardcoded styles to semantic tokens.
