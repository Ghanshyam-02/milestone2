# Task 5 - Deployment & Migration Strategy

## Approach

| Pattern | How we use it |
|---|---|
| Hybrid | Old on-prem system and new cloud run together. |
| Strangler Fig | Move one part at a time: Fraud first, then Reporting, then Finance. |
| Canary | Send 5% of traffic to the new system, then 25%, then 100%. |
| Blue-green | Keep the old version ready so we can switch back instantly. |
| Immutable infrastructure | Build servers from code (Terraform); replace them, don't patch them. |

We do **not** use a big-bang cutover.

## Migration sequence

![Migration phases](images/migration.png)

ON-PREM → HYBRID → CLOUD PILOT → DUAL RUN → VALIDATION → CUTOVER → DECOMMISSION

| Phase | What happens |
|---|---|
| On-prem | Record current numbers (volumes, totals, speed). |
| Hybrid | Connect on-prem to AWS and copy data with DMS. |
| Cloud pilot | Run fraud checks in the cloud for one country. |
| Dual run | Both systems run; on-prem is still the main one. |
| Validation | Compare results and test everything. |
| Cutover | Move traffic to the cloud step by step. |
| Decommission | Archive old data and switch off on-prem. |

## Checks

- **Cutover criteria:** row counts and totals match, fraud data in ≤ 30 s, API ≤ 500 ms, no major issues for 30 days.
- **Rollback criteria:** totals don't match, fraud data is late, API errors are high, or a serious incident happens.
- **Data reconciliation:** compare daily row counts and amount totals between on-prem and cloud.
- **API health checks:** `/health` endpoint checked every minute.
- **Smoke tests:** after each deployment, call the API once and check the response.
- **Monitoring:** CloudWatch alarms for delay, errors and response time.
- **Who approves cutover:** CTO with the Change Advisory Board (Fraud, Finance, Compliance and Security heads).
