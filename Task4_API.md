# Task 4 - API Contract & Testing

## What was asked

Create an API contract for `GET /analytics/payment-summary` with:
- an OpenAPI-style specification (endpoint, parameters, response, status codes, validation rules)
- a Pydantic model with validation
- at least 4 Gherkin scenarios

Our code for this task: `code/api.py` (FastAPI).

## The endpoint

`GET /analytics/payment-summary?period=2026-09&country=IN`

**Example response:**

```json
{
  "period": "2026-09",
  "country": "IN",
  "transaction_count": 120000,
  "successful_transactions": 112000,
  "success_rate": 93.33,
  "payment_volume": 458000000
}
```

| Field | Meaning |
|---|---|
| transaction_count | All payment attempts in the month |
| successful_transactions | Payments with status SUCCESS |
| success_rate | successful ÷ total × 100 (112,000 ÷ 120,000 = 93.33) |
| payment_volume | Total amount of successful payments |

## Parameters and status codes

| Parameter | Required | Rule | Example |
|---|---|---|---|
| period | Yes | YYYY-MM, month 01-12 | 2026-09 |
| country | Yes | 2 capital letters | IN |

| Code | When |
|---|---|
| 200 | Summary found |
| 400 | Period or country is in the wrong format |
| 401 | No login token |
| 403 | Logged in but not allowed |
| 404 | No data for that month and country |
| 500 | Server error |

## OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: PayShield Analytics API
  version: 1.0.0
paths:
  /analytics/payment-summary:
    get:
      summary: Monthly payment summary for a country
      parameters:
        - name: period
          in: query
          required: true
          schema: {type: string, pattern: '^\d{4}-(0[1-9]|1[0-2])$'}   # e.g. 2026-09
        - name: country
          in: query
          required: true
          schema: {type: string, pattern: '^[A-Z]{2}$'}                # e.g. IN
      responses:
        '200':
          description: Summary returned
          content:
            application/json:
              schema: {$ref: '#/components/schemas/PaymentSummary'}
        '400': {description: Invalid period or country}
        '401': {description: Not logged in}
        '403': {description: Not allowed}
        '404': {description: No data found}
        '500': {description: Server error}
components:
  schemas:
    PaymentSummary:
      type: object
      required: [period, country, transaction_count, successful_transactions, success_rate, payment_volume]
      properties:
        period: {type: string}
        country: {type: string}
        transaction_count: {type: integer, minimum: 0}
        successful_transactions: {type: integer, minimum: 0}
        success_rate: {type: number, minimum: 0, maximum: 100}
        payment_volume: {type: number, minimum: 0}
```

**Validation rules**
- `period` must be `YYYY-MM` (month 01-12).
- `country` must be 2 capital letters.
- All counts and the volume must be 0 or more.
- `success_rate` must be between 0 and 100.
- `successful_transactions` cannot be more than `transaction_count`.

## Pydantic Model

Pydantic checks the data automatically. If a rule is broken, it raises an error.

```python
from pydantic import BaseModel, Field, model_validator

class PaymentSummary(BaseModel):
    period: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    country: str = Field(pattern=r"^[A-Z]{2}$")
    transaction_count: int = Field(ge=0)
    successful_transactions: int = Field(ge=0)
    success_rate: float = Field(ge=0, le=100)
    payment_volume: float = Field(ge=0)

    @model_validator(mode="after")
    def check_counts(self):
        if self.successful_transactions > self.transaction_count:
            raise ValueError("successful_transactions cannot exceed transaction_count")
        return self
```

## Gherkin Scenarios

Gherkin describes tests in plain English: **Given** (the starting situation), **When** (the action), **Then** (the expected result).

```gherkin
Feature: Payment summary API

  Scenario: Return payment summary for valid country
    Given valid payment data exists
    When the client requests the India payment summary for 2026-09
    Then the API should return HTTP 200
    And success_rate should be between 0 and 100

  Scenario: Invalid period
    When the client requests the summary with period "2026-13"
    Then the API should return HTTP 400

  Scenario: Invalid country
    When the client requests the summary with country "india"
    Then the API should return HTTP 400

  Scenario: Request without login
    Given the client has no token
    When the client requests the India payment summary
    Then the API should return HTTP 401

  Scenario: No data for the period
    When the client requests the summary for period "2020-01"
    Then the API should return HTTP 404
```

## Result of `code/api.py` on our sample data

| Request | Response |
|---|---|
| period=2026-09, country=IN | 200 - 4 payments, 2 successful, 50.0%, volume 4,800 |
| period=2026-13, country=IN | 400 - invalid period |
| period=2020-01, country=IN | 404 - no data |
