# Script - Task 2: Physical Data Model

## What was asked
"In Task 2, we had to do three things. First, design a star schema with a payment fact table and four dimensions: customer, merchant, account and date, including keys, data types, constraints and partitioning. Second, explain how to keep the history of merchant risk, so that a February payment gets the February risk and not today's risk. Third, design a small Data Vault and explain why it helps the bank with audit."

## The theory
"A star schema is the most common design for reporting. It has one fact table in the middle, which holds the numbers like the payment amount. Around it are dimension tables, which hold the details: who the customer is, which merchant, which account and which date. The shape looks like a star.

The most important idea is the grain, which means what one row represents. In our fact table, one row is one payment attempt.

For history we use Slowly Changing Dimensions, or SCD. Type 1 simply overwrites the old value, so the history is lost. Type 2 closes the old row with an end date and adds a new row, so the full history is kept.

A Data Vault is another way to model data, built for history and audit. It has three kinds of table. Hubs hold only the business keys. Links hold the relationships. Satellites hold the details and every change to them."

## What we did
"For the star schema, we created five tables. Each dimension has a surrogate key, which is a number we create ourselves, like merchant_sk. We need it because merchant M100 has three versions of its risk, so the merchant ID alone is not unique. We used DECIMAL for money, because FLOAT causes rounding errors, and we added CHECK constraints for status, fraud decision and risk score. The fact table is partitioned by month, so a monthly report only reads one month of data.

For merchant risk, we chose SCD Type 2. M100 has three rows: LOW from January to March, HIGH from April to June and MEDIUM from July onwards. When we load a payment, we join on the merchant ID and check that the payment date falls between effective_from and effective_to. This is called a point-in-time join. We tested it on our sample data in pipeline.py. The February payment gets LOW, the May payment gets HIGH and the August payment gets MEDIUM, even though M100's current risk is MEDIUM.

For the Data Vault, we created three hubs, two links and three satellites. Every row has a load time and a record source."

## Why it matters
"The star schema makes reports fast and simple. SCD Type 2 makes sure every payment keeps the correct risk forever. The Data Vault never overwrites anything and records where each row came from, so auditors and regulators can always see exactly what we knew on any date. That solves the problem of reports that cannot be reproduced."
