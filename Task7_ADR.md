# Task 7 - Architecture Decision Record

## What was asked

The CTO asked: *"Why should we use this architecture instead of simply building another centralized warehouse?"*

Compare Kimball, Inmon, Data Vault, Lakehouse/Medallion and Data Mesh (strengths, weaknesses, complexity, governance, audit, scalability, suitability), without just saying one is best. Then write an ADR with: Decision, Context, Options Considered, Decision Drivers, Chosen Architecture, Consequences, Risks, Migration Approach and Rollback Approach.

## The five approaches in simple words

| Approach | In simple words |
|---|---|
| Kimball | Build star schemas (fact + dimensions) for reporting |
| Inmon | Build one big central warehouse first, then smaller marts from it |
| Data Vault | Hubs, links and satellites that keep every change for audit |
| Lakehouse / Medallion | Cheap file storage with database features, in Bronze/Silver/Gold layers |
| Data Mesh | Each business team owns and shares its own data |

## Comparison

| Approach | Strengths | Weaknesses | Suitability for PayShield |
|---|---|---|---|
| Kimball | Simple, fast for reports | Weak history, batch only | Good for the Gold layer |
| Inmon | One integrated source of truth | Slow and costly to build | Low |
| Data Vault | Full history, very good for audit | Many tables, hard to query | Good for history in Silver |
| Lakehouse / Medallion | Streaming + batch, scales, cheap storage | Needs good governance | **Best fit - main platform** |
| Data Mesh | Teams own their data | Complex, needs mature teams | Not now, maybe later |

| Approach | Complexity | Governance | Audit / Regulatory | Scalability |
|---|---|---|---|---|
| Kimball | Low | Central | Medium | Medium |
| Inmon | High | Central | Good | Medium |
| Data Vault | High | Central | Very good | Good |
| Lakehouse | Medium | Central | Good | Very good |
| Data Mesh | Very high | Shared by teams | Varies by team | Very good |

No single approach does everything, so we **combine** them.

## ADR-001: PayShield Data Platform

| Field | Content |
|---|---|
| **Status** | Accepted |
| **Decision** | Use a Lakehouse (Bronze/Silver/Gold) on AWS, with Data Vault history in Silver and a Kimball star schema in Gold. |
| **Context** | Fraud data is too slow (4-hour batch), reports cannot be reproduced, and the old system cannot handle 5,000 payments/sec. The old system cannot be switched off at once. |
| **Options considered** | Kimball, Inmon, Data Vault, Lakehouse, Data Mesh. |
| **Decision drivers** | Fraud data in ≤ 30 s; 5,000 payments/sec; 7-year audit history; reproducible reports; gradual migration; low cost. |
| **Chosen architecture** | Kinesis streaming + S3/Glue lakehouse (Bronze, Silver) + Redshift star schema (Gold) + API Gateway + QuickSight. |
| **Consequences (good)** | Fraud data in seconds, reports can be re-run, scales automatically, cheap storage. |
| **Consequences (bad)** | More services to manage, team needs new skills, cost of running two systems during migration. |
| **Risks** | Skills gap, cloud cost growing, data not matching during migration. Reduced by training, budget alarms and daily reconciliation. |
| **Migration approach** | Hybrid + Strangler Fig. Move one part at a time with a 30-day dual run (see Task 5). |
| **Rollback approach** | Keep the on-prem system running until the end. If there is a problem, send traffic back to it. |

## Answer to the CTO

**Why not just another central warehouse?**
1. A warehouse is **batch**, so it cannot give fraud data in 30 seconds.
2. It is **expensive to scale** for 5,000 payments/sec and 7 years of data.
3. It usually **overwrites data**, so old reports cannot be reproduced.

We still use a warehouse-style star schema in Gold for reports, but the lakehouse underneath gives us streaming, full history and cheap scaling.
