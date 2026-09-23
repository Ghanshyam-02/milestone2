# Task 4 - API Contract & Testing

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
        '200': {description: Summary returned}
        '400': {description: Invalid period or country}
        '401': {description: Not logged in}
        '403': {description: Not allowed}
        '404': {description: No data found}
        '500': {description: Server error}
```

**Validation rules**
- `period` must be `YYYY-MM` (month 01-12).
- `country` must be 2 capital letters.
- `success_rate` must be between 0 and 100.
- `successful_transactions` cannot be more than `transaction_count`.

## Pydantic Model

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

  Scenario: Request without login
    Given the client has no token
    When the client requests the India payment summary
    Then the API should return HTTP 401

  Scenario: No data for the period
    When the client requests the summary for period "2020-01"
    Then the API should return HTTP 404
```
