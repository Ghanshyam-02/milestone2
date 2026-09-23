"""
Simple Analytics API: GET /analytics/payment-summary
Run:   uvicorn api:app --reload        (from the code folder)
Open:  http://127.0.0.1:8000/analytics/payment-summary?period=2026-09&country=IN
"""
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DATA = Path(__file__).resolve().parents[1] / "data"
txn = pd.read_csv(DATA / "payment_transaction.csv", parse_dates=["transaction_ts"])

app = FastAPI(title="PayShield Analytics API")


@app.exception_handler(RequestValidationError)
def bad_input(request, exc):
    return JSONResponse(status_code=400, content={"detail": "Invalid period or country"})


class PaymentSummary(BaseModel):
    period: str
    country: str
    transaction_count: int = Field(ge=0)
    successful_transactions: int = Field(ge=0)
    success_rate: float = Field(ge=0, le=100)
    payment_volume: float = Field(ge=0)


@app.get("/analytics/payment-summary", response_model=PaymentSummary)
def payment_summary(
    period: str = Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),   # e.g. 2026-09
    country: str = Query(pattern=r"^[A-Z]{2}$"),                # e.g. IN
):
    rows = txn[(txn["transaction_ts"].dt.strftime("%Y-%m") == period) & (txn["country"] == country)]
    if rows.empty:
        raise HTTPException(status_code=404, detail="No data for this period and country")

    success = rows[rows["status"] == "SUCCESS"]
    return PaymentSummary(
        period=period,
        country=country,
        transaction_count=len(rows),
        successful_transactions=len(success),
        success_rate=round(100 * len(success) / len(rows), 2),
        payment_volume=round(success["amount"].sum(), 2),
    )
