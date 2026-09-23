"""
Simple Bronze -> Silver -> Gold pipeline using pandas.
Run:  python code/pipeline.py
"""
from pathlib import Path

import pandas as pd

pd.set_option("display.width", 120)

DATA = Path(__file__).resolve().parents[1] / "data"

# ---------------- BRONZE: read the raw files ----------------
txn = pd.read_csv(DATA / "payment_transaction.csv", parse_dates=["transaction_ts"])
events = pd.read_csv(DATA / "payment_event.csv", parse_dates=["event_ts", "ingestion_ts"])
settlement = pd.read_csv(DATA / "settlement.csv")
merchant_risk = pd.read_csv(DATA / "merchant_risk.csv")

# ---------------- SILVER: clean the data ----------------
# 1. Remove duplicate events (same event_id sent twice)
events = events.drop_duplicates(subset="event_id")

# 2. Put events in the order they HAPPENED (event_ts), not the order they arrived
events = events.sort_values(["transaction_id", "event_ts"])
events["event_order"] = events.groupby("transaction_id").cumcount() + 1

# 3. Find late events (arrived more than 5 minutes after they happened)
events["minutes_late"] = (events["ingestion_ts"] - events["event_ts"]).dt.total_seconds() / 60
print("Late events:")
print(events[events["minutes_late"] > 5][["event_id", "transaction_id", "event_type", "minutes_late"]], "\n")

# 4. Problem A: sum settlements per transaction BEFORE joining
wrong = txn.merge(settlement, on="transaction_id")["amount"].sum()
settled_per_txn = settlement.groupby("transaction_id", as_index=False)["settlement_amount"].sum()
right = txn[txn["transaction_id"].isin(settled_per_txn["transaction_id"])]["amount"].sum()
print(f"Problem A - wrong total (join then sum): {wrong:,.2f}")
print(f"Problem A - right total (sum then join): {right:,.2f}\n")

# ---------------- GOLD: business tables ----------------
# 5. Merchant risk at the time of the payment (SCD Type 2 point-in-time join)
fact = txn.merge(settled_per_txn, on="transaction_id", how="left")
fact["txn_date"] = fact["transaction_ts"].dt.strftime("%Y-%m-%d")
fact = fact.merge(merchant_risk, on="merchant_id", how="left")
fact = fact[(fact["txn_date"] >= fact["effective_from"]) & (fact["txn_date"] <= fact["effective_to"])]
print("Merchant M100 risk at the time of each payment:")
print(fact[fact["merchant_id"] == "M100"][["transaction_id", "txn_date", "risk_category"]], "\n")

# 6. Monthly payment summary per country (used by the API)
fact["period"] = fact["transaction_ts"].dt.strftime("%Y-%m")
fact["is_success"] = fact["status"] == "SUCCESS"
fact["success_amount"] = fact["amount"].where(fact["is_success"], 0)
summary = fact.groupby(["period", "country"]).agg(
    transaction_count=("transaction_id", "count"),
    successful_transactions=("is_success", "sum"),
    payment_volume=("success_amount", "sum"),
).reset_index()
summary["success_rate"] = (100 * summary["successful_transactions"] / summary["transaction_count"]).round(2)
print("Payment summary:")
print(summary)
