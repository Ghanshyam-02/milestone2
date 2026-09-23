# Script - Task 4: API Contract & Testing

## What was asked
"In Task 4, we had to create an API contract for GET /analytics/payment-summary. We needed three things: an OpenAPI specification with the endpoint, parameters, response, status codes and validation rules; a Pydantic model for the response with validation; and at least four Gherkin test scenarios."

## The theory
"An API contract is a clear agreement on how the API works: what you send, what you get back and what errors can happen. OpenAPI is the standard format for writing it. Writing the contract first means the frontend, backend and testing teams can all work in parallel.

Pydantic is a Python library that checks data. We define the fields and their rules, and Pydantic automatically rejects data that breaks them.

Gherkin describes tests in plain English with three words. Given is the starting situation, When is the action, and Then is the expected result. Business people can read it, and developers turn each scenario into an automated test.

HTTP status codes tell the client what happened: 200 means OK, 400 means bad input, 401 means not logged in, 403 means logged in but not allowed, 404 means no data, and 500 means a server error."

## What we did
"The endpoint takes two parameters. period must be in YYYY-MM format with a month from 01 to 12, and country must be two capital letters, like IN. It returns the transaction count, successful transactions, success rate and payment volume. Success rate is successful divided by total, times 100. For the example, 112,000 divided by 120,000 gives 93.33.

We wrote the OpenAPI specification with all status codes and a schema for the response.

In the Pydantic model, counts and volume must be zero or more, and the success rate must be between 0 and 100. We also added a custom check that successful transactions can never be more than the total.

We wrote five Gherkin scenarios: a valid request returns 200, an invalid period returns 400, an invalid country returns 400, no login returns 401, and no data returns 404.

Finally, we built the API in code/api.py using FastAPI. On our sample data, India for September 2026 returns 4 payments, 2 successful, a 50 percent success rate and a volume of 4,800. An invalid month returns 400, and a month with no data returns 404."

## Why it matters
"The strict validation keeps bad data out. For example, the regular expression on country also blocks SQL injection attempts before they reach the database. The Pydantic model makes sure wrong numbers never leave the API."
