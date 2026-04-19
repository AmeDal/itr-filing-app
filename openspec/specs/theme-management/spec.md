## Capability: Theme Management

### Requirement: Theme Persistence and Initialization
The system SHALL persist the user's selected theme in `localStorage` and initialize the correct theme on page load before the main application renders to prevent flashing.

#### Scenario: User arrives for the first time
- **WHEN** the user visits the application and no theme is stored in `localStorage`
- **THEN** the system SHALL apply the system default (`prefers-color-scheme`)
- **AND** if no system default is set, it SHALL default to `dark`

#### Scenario: Re-visiting user
- **WHEN** a user visits the application with a theme already saved in `localStorage`
- **THEN** the system SHALL immediately apply that theme on `documentElement`

### Requirement: Reactive Theme Switching
The system SHALL allow changing the theme at runtime by updating the `data-theme` attribute on the `documentElement`.

#### Scenario: Changing theme
- **WHEN** the user selects a new theme via the UI
- **THEN** the system SHALL update `data-theme` to the selected value
- **AND** update the `localStorage` key to persist the choice
