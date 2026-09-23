# Task 3 - Data Engineering & Spark

## Bronze → Silver → Gold

| Layer | What it holds |
|---|---|
| Bronze | Raw data exactly as received. Never changed. |
| Silver | Cleaned data: correct types, no duplicates, bad rows removed. |
| Gold | Business tables: star schema and summaries for reports and the API. |

## Handling data problems

| Problem | How we handle it |
|---|---|
| Late-arriving events | Report using `event_ts` (when it happened), not `ingestion_ts`. Wait 15 minutes for late data (watermark). Very late data is fixed by a nightly job. |
| Out-of-order events | Sort events by `event_ts`, not by arrival time. |
| Duplicate events | Keep only one row per `event_id`. |
| Failed records | Move bad rows to a quarantine table with the reason. |
| Schema changes | Allow only new optional columns. Keep raw data in Bronze. |
| Incremental processing | Process only new data using checkpoints and MERGE. |

**Out-of-order example:**

```sql
SELECT transaction_id, event_type, event_ts,
       ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY event_ts) AS event_order
FROM payment_event;
```

## Problem A - Double counting

Yes, the developer's query **double counts**. If a transaction has 2 settlement rows, the join repeats the payment twice, so `SUM(t.amount)` is doubled.

**Fix:** sum the settlements first, then join.

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

## Why is the Spark job slow? How to check

- **Spark UI:** find the slowest stage.
- **Skew:** if one task takes much longer than the others, one key (such as a big merchant) has too much data.
- **Shuffle:** joins move data across machines. A large shuffle is slow.
- **Partitions:** too few gives big slow tasks; too many gives overhead.
- **Pre-aggregation:** reduce rows (e.g. one row per transaction) before the join.
- **Repartitioning:** repartition big tables on the join key (`transaction_id`).

## Should we use a broadcast join?

**Yes, for MERCHANT_RISK.**

- It is small (a few thousand rows), so Spark can copy it to every machine.
- The big PAYMENT_EVENT table then does not need to be shuffled, which saves time.
- The join must still use `merchant_id =` (plus the date range), otherwise it becomes very slow.
- It does not fix the big join (PAYMENT_EVENT + PAYMENT_TRANSACTION). That one needs repartitioning and skew handling.

```python
from pyspark.sql.functions import broadcast
result = events.join(broadcast(merchant_risk), "merchant_id")
```
