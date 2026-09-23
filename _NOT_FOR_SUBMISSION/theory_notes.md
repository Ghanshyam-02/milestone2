# Theory Notes (not for submission)

Simple explanations to help you understand each task.

## Task 1 - Architecture
- **C4 Level 2** = a diagram of the main parts (APIs, databases, streams) and how they connect.
- **Batch** = process data every few hours (slow). **Streaming** = process each event as it arrives (fast).
- We use **Kinesis** (stream) so fraud gets data in seconds, and **S3** because it is cheap for long-term storage.

## Task 2 - Data Model
- **Star schema** = one fact table (numbers like amount) plus dimension tables (who, what, when).
- **Grain** = what one row means. Here: one payment attempt.
- **SCD Type 2** = when a value changes, keep the old row and add a new row with dates. Keeps history.
- **Data Vault** = hubs (keys), links (relationships), satellites (details and history). Good for audit.

## Task 3 - Data Engineering
- **Bronze** = raw, **Silver** = clean, **Gold** = ready for reports.
- **Late events:** use the time the event happened (`event_ts`), not when it arrived.
- **Double counting:** joining one payment to many settlements repeats the payment. Sum first, then join.
- **Broadcast join:** copy a small table to all machines so the big table does not move.
- **Skew:** one key has too much data, so one task is very slow.

## Task 4 - API
- **OpenAPI** = a document describing the API (URL, inputs, outputs, errors).
- **Pydantic** = Python library that checks data is valid.
- **Gherkin** = tests written as Given / When / Then.
- **401** = not logged in. **403** = logged in but not allowed.

## Task 5 - Migration
- **Strangler Fig** = replace the old system piece by piece.
- **Canary** = send a small % of users to the new version first.
- **Blue-green** = two environments; switch between them instantly.
- **Rollback** = go back to the old system if something breaks.

## Task 6 - Security
- **SQL injection** = attacker puts SQL code in the input. Fix it with parameterized queries.
- **SAST** = scan the code. **SCA** = scan the libraries. **DAST** = test the running app.
- **Secret scan** = find passwords in the code.

## Task 7 - ADR
- **ADR** = a short document explaining an architecture decision and why it was made.
- **Kimball** = star schemas. **Inmon** = one big central warehouse first.
- **Lakehouse** = cheap data lake storage with database features.
- **Data Mesh** = each team owns its own data.
