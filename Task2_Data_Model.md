# Task 2 - Physical Data Model

## What was asked

- **A.** A star schema with DIM_CUSTOMER, DIM_MERCHANT, DIM_ACCOUNT, DIM_DATE and FACT_PAYMENT, with primary keys, foreign keys, data types, constraints and partitioning.
- **B.** How to keep merchant risk history, so a February payment gets the February risk.
- **C.** A small Data Vault and why it helps the bank with audit and history.

## A. Star Schema

A star schema has one **fact table** in the middle (the numbers, e.g. amount) and **dimension tables** around it (the details: who, which merchant, which account, which date).

**FACT_PAYMENT grain = one payment transaction attempt.**
Grain means "what one row stands for". Every payment attempt is exactly one row.

![Star schema](images/star_schema.png)

| Table | Primary key | Main columns |
|---|---|---|
| DIM_DATE | date_key | full_date, year_month |
| DIM_CUSTOMER | customer_sk | customer_id, country, segment, risk_category |
| DIM_ACCOUNT | account_sk | account_id, customer_id |
| DIM_MERCHANT | merchant_sk | merchant_id, risk_category, effective_from, effective_to |
| FACT_PAYMENT | transaction_id | the 4 foreign keys + amount, currency, status, fraud_decision, risk_score |

**Key words**
- **Surrogate key (_sk):** a number we create. Needed because merchant M100 has several versions, so `merchant_id` alone is not unique.
- **Foreign key (FK):** links the fact table to a dimension.
- **DECIMAL for money:** never FLOAT, because FLOAT causes rounding errors.

```sql
CREATE TABLE dim_date (
  date_key   INT PRIMARY KEY,        -- 20260214
  full_date  DATE NOT NULL,
  year_month CHAR(7) NOT NULL        -- 2026-02
);

CREATE TABLE dim_customer (
  customer_sk   BIGINT PRIMARY KEY,
  customer_id   VARCHAR(20) NOT NULL,
  country       CHAR(2) NOT NULL,
  segment       VARCHAR(10) CHECK (segment IN ('Retail','Premium','SME')),
  risk_category VARCHAR(6)  CHECK (risk_category IN ('LOW','MEDIUM','HIGH'))
);

CREATE TABLE dim_account (
  account_sk  BIGINT PRIMARY KEY,
  account_id  VARCHAR(20) NOT NULL UNIQUE,
  customer_id VARCHAR(20) NOT NULL
);

CREATE TABLE dim_merchant (             -- SCD Type 2
  merchant_sk    BIGINT PRIMARY KEY,
  merchant_id    VARCHAR(20) NOT NULL,
  risk_category  VARCHAR(6) NOT NULL,
  risk_score     DECIMAL(5,4),
  effective_from DATE NOT NULL,
  effective_to   DATE NOT NULL DEFAULT '9999-12-31',
  is_current     BOOLEAN NOT NULL
);

CREATE TABLE fact_payment (
  transaction_id VARCHAR(36) PRIMARY KEY,
  date_key       INT    NOT NULL REFERENCES dim_date(date_key),
  customer_sk    BIGINT NOT NULL REFERENCES dim_customer(customer_sk),
  merchant_sk    BIGINT NOT NULL REFERENCES dim_merchant(merchant_sk),
  account_sk     BIGINT NOT NULL REFERENCES dim_account(account_sk),
  transaction_ts TIMESTAMP NOT NULL,
  amount         DECIMAL(18,2) NOT NULL CHECK (amount >= 0),
  currency       CHAR(3) NOT NULL,
  status         VARCHAR(10) CHECK (status IN ('SUCCESS','FAILED','REVERSED')),
  fraud_decision VARCHAR(7)  CHECK (fraud_decision IN ('APPROVE','DECLINE')),
  risk_score     DECIMAL(5,4) CHECK (risk_score BETWEEN 0 AND 1)
);
```

**Partitioning and indexing**

| What | Why |
|---|---|
| Partition `fact_payment` by month of `transaction_ts` | A monthly report reads only one month, not 7 years |
| Sort / cluster by `date_key` and `country` | Most queries filter by date and country |
| Index `dim_merchant (merchant_id, effective_from)` | Fast lookup of the right merchant version |
| Small dimension tables copied to every node (Redshift `DISTSTYLE ALL`) | Joins stay fast |

## B. Merchant Risk History

| Option | What it does | Our choice |
|---|---|---|
| SCD Type 1 | Overwrites the old value | No - history is lost, February would show MEDIUM |
| **SCD Type 2** | Closes the old row and adds a new row | **Yes - used in Gold** |
| Data Vault | Keeps every change with load time | Yes - used in Silver for audit |

With **SCD Type 2**, merchant M100 has 3 rows:

| merchant_sk | merchant_id | risk | effective_from | effective_to | is_current |
|---|---|---|---|---|---|
| 1 | M100 | LOW | 2026-01-01 | 2026-03-31 | false |
| 2 | M100 | HIGH | 2026-04-01 | 2026-06-30 | false |
| 3 | M100 | MEDIUM | 2026-07-01 | 9999-12-31 | true |

A payment is joined to the row whose date range contains the payment date (a **point-in-time join**):

```sql
SELECT t.transaction_id, m.merchant_sk, m.risk_category
FROM payment_transaction t
JOIN dim_merchant m
  ON  m.merchant_id = t.merchant_id
  AND CAST(t.transaction_ts AS DATE) BETWEEN m.effective_from AND m.effective_to;
```

**Result on our sample data** (`code/pipeline.py`):

| Transaction | Date | Risk given | Current risk |
|---|---|---|---|
| T001 | 14 Feb 2026 | **LOW** | MEDIUM |
| T002 | 20 May 2026 | **HIGH** | MEDIUM |
| T004 | 5 Aug 2026 | **MEDIUM** | MEDIUM |

The fact table stores `merchant_sk`, so the February payment stays linked to LOW forever.

## C. Data Vault

A Data Vault has 3 kinds of table:

| Type | Holds | Our tables |
|---|---|---|
| Hub | Only the business key | HUB_CUSTOMER, HUB_MERCHANT, HUB_TRANSACTION |
| Link | Relationships between hubs | LINK_CUSTOMER_TRANSACTION, LINK_MERCHANT_TRANSACTION |
| Satellite | Details and their history | SAT_CUSTOMER, SAT_MERCHANT, SAT_TRANSACTION |

```sql
CREATE TABLE hub_customer    (customer_hk CHAR(32) PRIMARY KEY, customer_id VARCHAR(20), load_ts TIMESTAMP, record_source VARCHAR(50));
CREATE TABLE hub_merchant    (merchant_hk CHAR(32) PRIMARY KEY, merchant_id VARCHAR(20), load_ts TIMESTAMP, record_source VARCHAR(50));
CREATE TABLE hub_transaction (transaction_hk CHAR(32) PRIMARY KEY, transaction_id VARCHAR(36), load_ts TIMESTAMP, record_source VARCHAR(50));

CREATE TABLE link_customer_transaction (link_hk CHAR(32) PRIMARY KEY, customer_hk CHAR(32), transaction_hk CHAR(32), load_ts TIMESTAMP, record_source VARCHAR(50));
CREATE TABLE link_merchant_transaction (link_hk CHAR(32) PRIMARY KEY, merchant_hk CHAR(32), transaction_hk CHAR(32), load_ts TIMESTAMP, record_source VARCHAR(50));

CREATE TABLE sat_customer    (customer_hk CHAR(32), load_ts TIMESTAMP, segment VARCHAR(10), risk_category VARCHAR(6), PRIMARY KEY (customer_hk, load_ts));
CREATE TABLE sat_merchant    (merchant_hk CHAR(32), load_ts TIMESTAMP, risk_category VARCHAR(6), risk_score DECIMAL(5,4), PRIMARY KEY (merchant_hk, load_ts));
CREATE TABLE sat_transaction (transaction_hk CHAR(32), load_ts TIMESTAMP, amount DECIMAL(18,2), status VARCHAR(10), PRIMARY KEY (transaction_hk, load_ts));
```

- `_hk` is a hash key (MD5 of the business key).
- `load_ts` = when the row was loaded. `record_source` = which system it came from.

**Why Data Vault helps the bank**
- **Nothing is overwritten.** Rows are only inserted, so the full history is always there for auditors.
- **We know where data came from.** Every row has `load_ts` and `record_source` (on-prem or AWS).
- **Old reports can be rebuilt** exactly as they were on any date.
- **Easy to add new sources** without changing existing tables.

The downside is that it has many tables and is hard to query, so business users use the Gold star schema instead.
