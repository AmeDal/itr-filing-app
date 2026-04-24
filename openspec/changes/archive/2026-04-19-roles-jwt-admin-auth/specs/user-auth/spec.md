## MODIFIED Requirements

### Requirement: Tokenized Login Response
The login endpoint must return a JWT token pair instead of a simple user profile object.

#### Scenario: User provides valid credentials
- **WHEN** the login request is successful
- **THEN** the response must conform to the `AuthResponse` schema, containing tokens and a user summary, and set the refresh cookie.
