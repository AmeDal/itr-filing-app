## Capability: Theme Management

### Requirement: Theme Persistence and Initialization
The system SHALL persist the user's selected theme in `localStorage` and initialize the theme before the React app renders.

#### Scenario: User arrives for the first time
- **WHEN** the user visits the application and no theme is stored in `localStorage`
- **THEN** the inline script applies `dark` if `prefers-color-scheme: dark` matches
- **AND** otherwise applies `light`.

#### Scenario: Re-visiting user
- **WHEN** a user visits the application with a theme saved in `localStorage`
- **THEN** the inline script applies that value to `documentElement` before the main application renders.

### Requirement: Reactive Theme Switching
The system SHALL allow changing the theme at runtime by updating the `data-theme` attribute on `documentElement`.

#### Scenario: Changing theme
- **WHEN** the user toggles the theme
- **THEN** `AuthContext` updates the `data-theme` attribute
- **AND** updates the `localStorage` key to persist the choice.
