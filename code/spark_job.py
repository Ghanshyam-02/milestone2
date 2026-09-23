"""
Simple Spark job: join payments with events and merchant risk.
Shows duplicate removal, pre-aggregation and a broadcast join.
Run:  python code/spark_job.py      (needs pyspark and Java)
"""
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DATA = str(Path(__file__).resolve().parents[1] / "data")

spark = SparkSession.builder.master("local[*]").appName("payshield").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

txn = spark.read.csv(f"{DATA}/payment_transaction.csv", header=True, inferSchema=True)
events = spark.read.csv(f"{DATA}/payment_event.csv", header=True, inferSchema=True)
risk = spark.read.csv(f"{DATA}/merchant_risk.csv", header=True)

# 1. Remove duplicate events
events = events.dropDuplicates(["event_id"])

# 2. Pre-aggregate: one row per transaction before the join (less data to shuffle)
event_count = events.groupBy("transaction_id").agg(F.count("*").alias("event_count"))
payments = txn.join(event_count, "transaction_id", "left")

# 3. Broadcast join: merchant_risk is small, so copy it to every worker.
#    Join on merchant_id AND the date range (SCD Type 2).
p = payments.alias("p")
r = F.broadcast(risk).alias("r")
result = p.join(
    r,
    (F.col("p.merchant_id") == F.col("r.merchant_id"))
    & (F.to_date("p.transaction_ts").between(F.to_date("r.effective_from"), F.to_date("r.effective_to"))),
    "left",
)

result.select("p.transaction_id", "p.transaction_ts", "p.merchant_id", "r.risk_category", "event_count") \
      .orderBy("p.transaction_id").show()

# Look for "BroadcastHashJoin" in the plan
result.explain()

spark.stop()
