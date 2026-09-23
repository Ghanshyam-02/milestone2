# Script - Task 3: Data Engineering & Spark

## What was asked
"In Task 3, we had to design the Bronze, Silver and Gold processing. We had to explain how to handle late events, out-of-order events, duplicates, failed records, schema changes and incremental processing. We also had to explain how to investigate a slow Spark job, and whether to use a broadcast join for the merchant risk table."

## The theory
"The medallion architecture has three layers. Bronze stores raw data exactly as received and never changes it, so we can always reprocess if something goes wrong. Silver is the cleaned data. Gold is the business-ready data for reports.

Every event has two times. event_ts is when it actually happened. ingestion_ts is when it reached us. Reports must always use event_ts. A watermark is how long the streaming job waits for late events before closing a time window.

In Spark, a shuffle is when data moves between machines during a join. It is the slowest thing Spark does. Skew means one key has much more data than the others, so one task runs much longer than the rest. A broadcast join copies a small table to every machine, so the big table does not need to move."

## What we did
"We created sample data with these problems built in and wrote pipeline.py and spark_job.py.

Late events: payment T002's fraud event happened at 10:03 but arrived at 10:17, and T003's settlement arrived the next day. We report by event_ts, wait 15 minutes in streaming, and fix anything later with a nightly job.

Out-of-order events: T001's events arrived as AUTH, SETTLEMENT, FRAUD. We sort by event_ts, which gives the real order: AUTH, FRAUD, SETTLEMENT.

Duplicates: event E010 was sent twice, so we keep only one row per event_id.

Failed records go to a quarantine table with the reason. For schema changes, we only allow new optional columns. For incremental processing, we process only new data using checkpoints and MERGE.

Problem A: the developer's query joins payments to settlements and then sums. Some payments have two settlement rows, so the payment is counted twice. On our data the wrong total was 18,718.50 and the correct total was 16,148.50. The fix is to sum settlements per transaction first, then join.

For a slow Spark job, we would open the Spark UI, find the slowest stage, look for skew and large shuffles, check the partition sizes, pre-aggregate events before the join, and repartition the big tables on transaction_id."

## Broadcast join answer
"Yes, we should broadcast MERCHANT_RISK, because it only has a few thousand rows. Spark copies it to every machine, so the millions of event rows don't need to be shuffled. But we must still join on merchant_id as well as the date range, and it does not fix the other big join between events and transactions. That one needs pre-aggregation and repartitioning. Our Spark job shows 'BroadcastHashJoin' in its plan and gives the correct risk for each payment."
