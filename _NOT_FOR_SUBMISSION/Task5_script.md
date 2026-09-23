# Script - Task 5: Deployment & Migration Strategy

## What was asked
"In Task 5, the problem was that the old payment system cannot be switched off immediately. We had to design a migration using patterns like Hybrid, Strangler Fig, Canary and Blue-green. We then had to define seven phases, from on-prem to decommission, along with the cutover criteria, rollback criteria, data reconciliation, health checks, smoke tests, monitoring and who approves the final switch."

## The theory
"There are several deployment patterns.

- Greenfield means building something completely new.
- Hybrid means the old on-prem system and the new cloud system run together.
- Strangler Fig means replacing the old system piece by piece, like a vine that slowly grows around a tree until the tree is gone.
- Rolling deployment updates servers a few at a time.
- Blue-green keeps two full copies, so traffic can be switched between them instantly.
- Canary sends a small percentage of users to the new version first, to catch problems early.
- Immutable infrastructure means we never patch servers. We rebuild them from code.

The opposite of all this is a big-bang cutover, where everything switches on one day. That is too risky for a bank."

## What we did
"We chose Hybrid plus Strangler Fig as our main strategy, with Canary to move traffic slowly and Blue-green so we can switch back instantly.

We move one part at a time: fraud first, because it is read-only and gives the biggest benefit, then reporting, then finance, and payment intake last, because it is the most critical.

The seven phases are:
1. On-prem: we record today's numbers as a baseline.
2. Hybrid: we connect on-prem to AWS and copy data with DMS.
3. Cloud pilot: we run fraud checks in AWS for one country.
4. Dual run: both systems run for all countries, but on-prem is still the main one.
5. Validation: we compare results and test everything.
6. Cutover: we move traffic to AWS step by step, 5 percent, then 25, then 100.
7. Decommission: we archive the old data for seven years and switch off on-prem.

To cut over, row counts and totals must match, fraud data must arrive within 30 seconds, the API must answer within 500 milliseconds, and we need 30 days without problems.

We roll back if totals don't match, fraud data is late, API errors go above 1 percent, or there is a serious incident. Rollback is easy because the old system keeps running until the very end, so we just send traffic back to it.

Every day we reconcile row counts and totals between the two systems. The health endpoint is checked every minute, a smoke test runs after every deployment, and CloudWatch alarms watch for delays and errors.

The CTO gives the final approval, together with the Change Advisory Board: the heads of Fraud, Compliance, Finance and Security."
