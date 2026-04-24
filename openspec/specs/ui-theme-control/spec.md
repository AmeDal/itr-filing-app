## Capability: UI Theme Control

### Requirement: Theme Toggle Component
The system SHALL provide a visible UI component to toggle between light and dark modes.

#### Scenario: Switching from Dark to Light
- **WHEN** the user clicks the toggle while in `dark` mode
- **THEN** the system SHALL switch to `light` mode
- **AND** the icon SHALL update to represent the current or next state (e.g., Sun/Moon)

#### Scenario: Visual Feedback
- **WHEN** the theme is changed
- **THEN** all elements using semantic tokens SHALL update their appearance instantly to match the new theme's color palette
