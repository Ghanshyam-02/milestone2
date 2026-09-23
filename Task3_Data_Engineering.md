# Task 3 - Data Engineering & Spark

## What was asked

- Design the Bronze → Silver → Gold processing.
- Explain how to handle late events, out-of-order events, duplicates, failed records, schema changes and incremental processing.
- Explain how to investigate a slow Spark job (partitions, shuffle, skew, Spark UI, broadcast join, repartitioning, pre-aggregation).
- Answer: should we broadcast MERCHANT_RISK, and why?

Our code for this task: `code/pipeline.py` (pandas) and `code/spark_job.py` (Spark), using the sample files in `data/`.

## Bronze → Silver → Gold

| Layer | What it holds | What we do there |
|---|---|---|
| **Bronze** | Raw data exactly as received | Save everything, never change it. Lets us re-run if something goes wrong. |
| **Silver** | Clean data | Fix types, remove duplicates, order events, move bad rows to quarantine, apply SCD Type 2 |
| **Gold** | Business data | Star schema and monthly summary for reports and the API |

## Handling data problems

| Problem | How we handle it | Example in our sample data |
|---|---|---|
| Late-arriving events | Report using `event_ts` (when it happened), not `ingestion_ts` (when it arrived). The stream waits 15 minutes (watermark). Later data is merged by a nightly job. | T002 fraud event happened 10:03, arrived 10:17 (14 min late). T003 settlement happened 31 Aug, arrived 1 Sep. |
| Out-of-order events | Sort by `event_ts` and number the events per transaction | T001 arrived AUTH → SETTLEMENT → FRAUD, but happened AUTH → FRAUD → SETTLEMENT |
| Duplicate events | Keep only one row per `event_id` | E010 was sent twice |
| Failed records | Move bad rows to a quarantine table with the reason. Never delete silently. | e.g. negative amount, missing ID |
| Schema changes | Allow only new optional columns. Raw data stays in Bronze. | - |
| Incremental processing | Process only new data using checkpoints and MERGE | - |

**Ordering events by business time:**

```sql
SELECT transaction_id, event_type, event_ts,
       ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY event_ts) AS event_order
FROM payment_event;
```

## Problem A - Double counting

The developer's query:

```sql
SELECT t.transaction_id, SUM(t.amount), SUM(s.settlement_amount)
FROM payment_transaction t
JOIN settlement s ON t.transaction_id = s.transaction_id
GROUP BY t.transaction_id;
```

**Yes, it double counts.** One payment can have 2 settlement rows (partial settlement or correction). The join repeats the payment for each settlement row, so `SUM(t.amount)` is counted twice.

**Fix:** sum the settlements per transaction first, then join.

```sql
WITH s AS (
  SELECT transaction_id, SUM(settlement_amount) AS settlement_amount
  FROM settlement
  GROUP BY transaction_id
)
SELECT t.transaction_id, t.amount AS payment_amount, s.settlement_amount
FROM payment_transaction t
LEFT JOIN s ON s.transaction_id = t.transaction_id;
```

**Result on our sample data:** wrong total **18,718.50**, correct total **16,148.50** (T001 and T005 were counted twice).

## Why is the Spark job slow? How to check

| Step | What to look at |
|---|---|
| 1. Spark UI | Open the Stages tab and find the slowest stage |
| 2. Skew | One task takes much longer than the others, because one key (e.g. a big merchant) has too much data |
| 3. Shuffle | Joins move data between machines. Big shuffle read/write means slow |
| 4. Partitions | Too few gives huge tasks; too many gives overhead. Aim for about 128-256 MB each |
| 5. Pre-aggregation | Reduce rows before joining (e.g. one row per transaction instead of many events) |
| 6. Repartitioning | Repartition the big tables on the join key (`transaction_id`) |
| 7. Broadcast join | Copy small tables to every machine (see below) |

## Should we use a broadcast join?

**Yes, for MERCHANT_RISK, but it is not the full fix.**

- **Why yes:** MERCHANT_RISK has only a few thousand rows. Spark can copy it to every machine. Then the millions of PAYMENT_EVENT rows do not need to be shuffled for this join.
- **Keep an equality key:** join on `merchant_id =` plus the date range. A join on only a date range becomes very slow.
- **Check the size:** if the table grows very large, broadcasting uses too much memory.
- **Not the full fix:** the big join (PAYMENT_EVENT + PAYMENT_TRANSACTION) cannot be broadcast. It needs pre-aggregation, repartitioning and skew handling.

```python
from pyspark.sql import functions as F

result = payments.join(
    F.broadcast(risk),
    (payments.merchant_id == risk.merchant_id)
    & F.to_date(payments.transaction_ts).between(F.to_date(risk.effective_from), F.to_date(risk.effective_to)),
    "left",
)
```

**Result of the Spark job** (`code/spark_job.py`): the Spark plan shows `BroadcastHashJoin`, and M100 gets LOW (Feb), HIGH (May) and MEDIUM (Aug).
