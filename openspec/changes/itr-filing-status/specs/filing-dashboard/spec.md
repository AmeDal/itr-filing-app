## ADDED Requirements

### Requirement: View filing history
Users must be able to see a list of all their filing attempts.

#### Scenario: Listing attempts
- **WHEN** a user navigates to the History page
- **THEN** the system returns all documents from `filing_attempts` for that user.

### Requirement: Direct document re-upload
Users can trigger a re-upload for any document from the dashboard.

#### Scenario: Triggering re-upload
- **WHEN** a user clicks "Re-upload" on a document
- **THEN** they can select a new file which follows the recovery/replacement logic.
