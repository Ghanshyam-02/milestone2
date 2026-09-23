Case Study: PayShield — Real-Time Fraud & Regulatory Data Platform Modernisation

1. Business Scenario

PayShield Bank operates a cross-border card-payment platform.

The current system is an on-premise application that processes card transactions and sends transaction data to:

Fraud Detection
Regulatory Reporting
Finance/Settlement
Customer Analytics
The bank is facing three problems:

Fraud decisions are taking too long during peak hours.
Regulatory reports are difficult to reproduce because source data changes after reporting.
The existing platform cannot scale efficiently during large payment spikes.
The CTO has therefore approved a hybrid cloud modernisation.

Current Architecture

┌──────────────────┐

Card Channels ────► │ On-Prem Payment │

│ Application │

└────────┬─────────┘

|

┌──────────────┼──────────────┐

↓ ↓ ↓

Fraud DB Reporting DB Finance DB

|

Batch ETL every 4 hours

The target platform should support:

Payment Channels

|

v

Payment API

|

+----------------------+

| |

v v

Real-time Fraud Event Stream

|

v

Cloud Data Platform

Bronze/Silver/Gold

/ \

/ \

Regulatory Analytics API

Reporting |

v

Web Dashboard

The CTO wants the new platform to be cloud-ready, scalable, auditable and secure, but the bank cannot immediately switch off the existing on-premise system.

2. Available Information

The following simplified data sources are available.

PAYMENT_TRANSACTION

Column

Description

transaction_id

Unique payment attempt

customer_id

Customer

merchant_id

Merchant

account_id

Funding account

transaction_ts

Business transaction time

amount

Transaction amount

currency

Transaction currency

country

Transaction country

status

SUCCESS / FAILED / REVERSED

fraud_decision

APPROVE / DECLINE

risk_score

0–1

Expected grain:

One row = one payment transaction attempt.

PAYMENT_EVENT

Column

Description

event_id

Unique event

transaction_id

Payment transaction

event_type

AUTH / FRAUD / SETTLEMENT / REVERSAL

event_ts

Event occurrence time

ingestion_ts

Event arrival time

processing_ms

Processing duration

One transaction can have multiple events.

CUSTOMER

Column

Description

customer_id

Customer

country

Customer country

segment

Retail / Premium / SME

risk_category

LOW / MEDIUM / HIGH

MERCHANT_RISK

Column

Description

merchant_id

Merchant

effective_from

Risk validity start

effective_to

Risk validity end

risk_category

LOW / MEDIUM / HIGH

risk_score

Merchant risk

This table maintains historical versions of merchant risk.

SETTLEMENT

Column

Description

settlement_id

Settlement record

transaction_id

Transaction

settlement_ts

Settlement time

settlement_amount

Settled amount

settlement_currency

Currency

fee_amount

Processing fee

A transaction can have multiple settlement records because of partial settlement or correction.

3. Deliberate Problems Hidden in the Data

The learner is not explicitly told how to fix these.

During investigation they discover:

Problem A — One-to-many inflation

A developer created:

SELECT

t.transaction_id,

SUM(t.amount) AS payment_amount,

SUM(s.settlement_amount) AS settlement_amount

FROM payment_transaction t

JOIN settlement s

ON t.transaction_id = s.transaction_id

GROUP BY t.transaction_id;

Some transactions have multiple settlement records.

The learner must determine whether this creates double counting.

Problem B — Late-arriving events

Some events have:

event_ts = 10:03

ingestion_ts = 10:17

Others arrive the following day.

The business currently reports using only ingestion_ts.

Problem C — Out-of-order events

Example:

AUTH 10:01

SETTLEMENT 10:04

FRAUD 10:02

The events were received in a different order from when they occurred.

Problem D — Merchant Risk SCD

Merchant risk changes over time:

Merchant M100

LOW Jan 1 – Mar 31

HIGH Apr 1 – Jun 30

MEDIUM Jul 1 onwards

A transaction from February must not automatically receive the July risk category.

Problem E — Performance

During peak periods:

Normal volume: 500 transactions/sec

Peak volume: 5,000 transactions/sec

The existing batch architecture takes 4 hours to process the previous day's data.

The fraud team requires:

Fraud data available within 30 seconds.

Problem F — API Security

The proposed API contains:

@app.get("/customer/{customer_id}")

def get_customer(customer_id):

query = f"""

SELECT * FROM customer

WHERE customer_id = '{customer_id}'

"""

The learner must identify the security concern.

4. Business Requirement

The CTO gives the engineering team the following requirement:

"Design a cloud-ready platform that can process payment events in near real time, preserve regulatory history, expose trusted payment analytics through an API, and allow the bank to migrate gradually from on-premise to cloud."

The target must support:

Functional requirements

Payment ingestion
Fraud analytics
Regulatory reporting
Historical auditability
Analytics API
Dashboard consumption
Non-functional requirements

Requirement

Target

Peak transactions

5,000/sec

Fraud data availability

≤30 sec

API response

≤500 ms for normal queries

Availability

99.9%

Historical retention

7 years

Deployment

Dev → Test → Prod

Migration

No big-bang cutover

Rollback

Required

5. Candidate Tasks

Task 1 — Architecture & Cloud Design

Design the target architecture.

The candidate must produce a C4 Level 2 Container Diagram covering:

Payment Channels

↓

Payment API

↓

Streaming

↓

Bronze

↓

Silver

↓

Gold

↓

Analytics API

↓

Dashboard

The design must identify:

Compute
Storage
Streaming
Lakehouse
API layer
Identity
Secrets
Monitoring
Governance
Cloud choice

The bank has shortlisted:

AWS or Azure

The learner must select one and map at least 8 services.

Example:

Capability

AWS

Azure

Compute

ECS/EKS/Lambda

Container Apps/AKS/Functions

Storage

S3

ADLS Gen2

Streaming

Kinesis/MSK

Event Hubs

Lakehouse

Glue/EMR/Athena

Databricks/Data Factory

Identity

IAM

Entra ID

Secrets

Secrets Manager

Key Vault

Monitoring

CloudWatch

Azure Monitor

API

API Gateway

API Management

Important

The candidate must explain why the selected architecture fits the workload, rather than simply listing cloud services.

Task 2 — Physical Data Model & Data Architecture

Produce:

A. Star schema

DIM_CUSTOMER

DIM_MERCHANT

DIM_ACCOUNT

DIM_DATE

|

|

FACT_PAYMENT

Explicitly state:

FACT_PAYMENT grain = one payment transaction attempt.

Define:

Primary keys
Foreign keys
Data types
Constraints
Important indexes/clustering/partitioning strategy
B. Handle historical merchant risk

Explain whether the solution should use:

SCD Type 1
SCD Type 2
Data Vault
another approach
The candidate must show how a transaction from February gets the correct merchant risk even when the merchant's current risk is MEDIUM.

C. Data Vault consideration

Create a small Data Vault design containing:

HUB_CUSTOMER

HUB_MERCHANT

HUB_TRANSACTION

LINK_CUSTOMER_TRANSACTION

LINK_MERCHANT_TRANSACTION

SAT_CUSTOMER

SAT_MERCHANT

SAT_TRANSACTION

The candidate does not need to implement the entire Vault.

They must explain:

Why might Data Vault be useful for this bank's audit/history requirements?

Task 3 — Data Engineering & Spark Investigation

Design the Bronze → Silver → Gold processing.

Raw Events

↓

Bronze

↓

Silver

↓

Gold

Explain how you would handle:

late-arriving events
out-of-order events
duplicate events
failed records
schema changes
incremental processing
Spark requirement

A Spark job joins:

PAYMENT_EVENT

JOIN

PAYMENT_TRANSACTION

JOIN

MERCHANT_RISK

The job becomes extremely slow during peak periods.

The learner must explain how they would investigate:

partitions
shuffle
skew
Spark UI
broadcast join
repartitioning
pre-aggregation
Critical question

PAYMENT_EVENT contains millions of rows, while MERCHANT_RISK contains only a few thousand current/historical records.

Should the candidate consider a broadcast join?

They must explain why or why not, rather than simply answering yes.

Task 4 — API Contract + Testing

Create an API contract for:

GET /analytics/payment-summary

Expected response:

{

"period": "2026-09",

"country": "IN",

"transaction_count": 120000,

"successful_transactions": 112000,

"success_rate": 93.33,

"payment_volume": 458000000

}

The candidate must provide:

OpenAPI-style specification

Include:

endpoint
parameters
response
HTTP status codes
validation rules
Pydantic model

Define the response structure.

For example:

class PaymentSummary(BaseModel):

period: str

country: str

transaction_count: int

successful_transactions: int

success_rate: float

payment_volume: float

Add appropriate validation.

Acceptance criteria

Write at least 4 Gherkin scenarios.

Example:

Scenario: Return payment summary for valid country

Given valid payment data exists

When the client requests the India payment summary

Then the API should return HTTP 200

And success_rate should be between 0 and 100

Task 5 — Deployment & Migration Strategy

The existing payment system cannot be switched off immediately.

Design a migration approach.

The candidate must choose and explain a combination of:

Greenfield
Hybrid
Strangler Fig
Rolling deployment
Blue-green
Canary
Immutable infrastructure
Required output

Create this sequence:

ON-PREM

↓

HYBRID

↓

CLOUD PILOT

↓

DUAL RUN

↓

VALIDATION

↓

CUTOVER

↓

DECOMMISSION

Define:

cutover criteria
rollback criteria
data reconciliation
API health checks
smoke tests
monitoring
who approves production cutover
Task 6 — Security & DevSecOps

The candidate receives this code:

@app.get("/customer/{customer_id}")

def get_customer(customer_id):

query = f"""

SELECT *

FROM customer

WHERE customer_id = '{customer_id}'

"""

return execute(query)

Identify the security weaknesses.

Then propose controls covering:

Secure Coding

input validation
parameterized SQL
authentication
authorization
RBAC
secrets management
PII protection
secure logging
Pipeline

Design:

Developer Branch

↓

Unit Tests

↓

SAST

↓

Secret Scan

↓

SCA

↓

Docker Build

↓

Container Scan

↓

DAST

↓

Approval

↓

Production

Identify which failures should block the pipeline.

Task 7 — Architecture Decision Record

The CTO asks:

"Why should we use this architecture instead of simply building another centralized warehouse?"

The candidate must compare:

Approach

Suitability

Kimball

Inmon

Data Vault

Lakehouse/Medallion

Data Mesh

The candidate must not simply say one is best.

Instead, provide:

strengths
weaknesses
operational complexity
governance implications
regulatory/audit implications
scalability
suitability for PayShield
Then make an ADR containing:

Decision

Context

Options Considered

Decision Drivers

Chosen Architecture

Consequences

Risks

Migration Approach

Rollback Approach