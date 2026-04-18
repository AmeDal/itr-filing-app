## ADDED Requirements

### Requirement: Async MongoDB Integration
The system must use a non-blocking driver to communicate with MongoDB.

#### Scenario: Database operation during request
- **WHEN** an API request requires a database write (e.g., signup)
- **THEN** the system must await the operation using `motor` without blocking the main event loop.

### Requirement: IST Timezone Consistency
All temporal metadata stored in the database must be in Indian Standard Time (UTC+5:30).

#### Scenario: Document or User creation
- **WHEN** a new record is inserted into any collection
- **THEN** the `created_at` field must be populated with the current IST time.
