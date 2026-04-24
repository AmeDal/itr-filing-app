## Capability: UI Theme Control

### Requirement: Theme Toggle Component
The system SHALL provide a visible UI component to toggle between light and dark modes.

#### Scenario: Switching themes
- **WHEN** the user clicks `ThemeToggle`
- **THEN** the app switches between `light` and `dark` modes
- **AND** the icon changes between Sun and Moon states.

#### Scenario: Visual feedback
- **WHEN** the theme is changed
- **THEN** elements using semantic theme tokens update their appearance to match the current theme.
