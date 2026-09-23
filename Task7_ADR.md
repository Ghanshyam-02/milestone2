# Task 7 - Architecture Decision Record

## Comparison

| Approach | Strengths | Weaknesses | Suitability for PayShield |
|---|---|---|---|
| Kimball | Simple, fast for reports | Weak history, batch only | Good for Gold layer |
| Inmon | One integrated source of truth | Slow and costly to build | Low |
| Data Vault | Full history, good for audit | Many tables, hard to query | Good for history in Silver |
| Lakehouse / Medallion | Streaming + batch, scales, cheap storage | Needs good governance | **Best fit - main platform** |
| Data Mesh | Teams own their data | Complex, needs mature teams | Not now, maybe later |

| Approach | Complexity | Governance | Audit | Scalability |
|---|---|---|---|---|
| Kimball | Low | Central | Medium | Medium |
| Inmon | High | Central | Good | Medium |
| Data Vault | High | Central | Very good | Good |
| Lakehouse | Medium | Central | Good | Very good |
| Data Mesh | Very high | Shared by teams | Varies | Very good |

## ADR-001: PayShield Data Platform

**Decision:** Use a Lakehouse (Bronze/Silver/Gold) on AWS, with Data Vault history in Silver and a Kimball star schema in Gold.

**Context:** Fraud data is too slow, reports cannot be reproduced, and the old system cannot handle peak load.

**Options considered:** Kimball, Inmon, Data Vault, Lakehouse, Data Mesh.

**Decision drivers:** fraud data in 30 seconds, 5,000 transactions/sec, 7-year audit history, gradual migration.

**Chosen architecture:** Kinesis streaming + S3/Glue lakehouse + Redshift star schema + API Gateway.

**Consequences:** faster fraud checks, reproducible reports and easy scaling, but more services to manage and new skills needed.

**Risks:** team skills gap, cloud cost, data mismatch during migration.

**Migration approach:** Hybrid + Strangler Fig. Move one part at a time with a dual run (see Task 5).

**Rollback approach:** keep the on-prem system running until the end and switch traffic back if there is a problem.

**Why not just another central warehouse?** A warehouse is batch, so it cannot give fraud data in 30 seconds. It is also costly to scale and does not keep raw history for audit.
