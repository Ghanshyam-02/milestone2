# Script - Task 7: Architecture Decision Record

## What was asked
"In Task 7, the CTO asked: why should we use this architecture instead of simply building another central data warehouse? We had to compare five approaches, Kimball, Inmon, Data Vault, Lakehouse and Data Mesh, fairly, without just saying one is the best. Then we had to write an Architecture Decision Record, or ADR."

## The theory
"An ADR is a short document that records one important decision: why it was made, which options were considered and what the consequences are. It helps people who join later understand why the system looks the way it does.

The five approaches are:
- Kimball builds star schemas for reporting. It is simple and fast, but keeps limited history and is usually batch.
- Inmon builds one big, fully integrated central warehouse first. It is consistent but slow and costly to build.
- Data Vault uses hubs, links and satellites and keeps every change. It is excellent for audit but hard to query.
- A Lakehouse with Medallion layers stores data cheaply as files but adds database features. It supports streaming and batch and scales very well, but it needs good governance.
- Data Mesh gives each business team ownership of its own data. It scales across a big organisation but needs mature teams."

## What we did
"We compared all five on strengths, weaknesses, complexity, governance, audit and scalability. We found that no single approach meets all of PayShield's needs, so we combined them, using each one where it is strongest.

Our decision: a Lakehouse with Bronze, Silver and Gold layers on AWS. The Silver layer uses Data Vault ideas to keep full history for audit, and the Gold layer uses a Kimball star schema for fast reports. Data Mesh is a good option for the future, but not now, because the bank does not yet have teams ready to own their data and it would add risk during the migration.

In the ADR, the context is slow fraud data, reports that cannot be reproduced and a system that cannot scale. The decision drivers are fraud data in 30 seconds, 5,000 payments per second, seven years of audit history and a gradual migration. The good consequences are faster fraud checks, reproducible reports and automatic scaling. The downsides are more services to manage, new skills to learn and the cost of running two systems during migration. For migration we use Hybrid plus Strangler Fig, and for rollback we keep the old system running until the end."

## Answer to the CTO
"So why not just another warehouse? Three reasons. First, a warehouse is batch, so it cannot give fraud data in 30 seconds. Second, it is expensive to scale to 5,000 payments per second and seven years of data. Third, it usually overwrites data, so old reports cannot be reproduced. We still use a warehouse-style star schema in the Gold layer, but the lakehouse underneath gives us streaming, full history and cheap scaling."
