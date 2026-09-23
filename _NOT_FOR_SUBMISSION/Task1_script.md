# Script - Task 1: Architecture & Cloud Design

## What was asked
"In Task 1, we were asked to design the new cloud architecture for PayShield Bank. We had to draw a C4 Level 2 container diagram showing the flow from payment channels, through the payment API, streaming, the Bronze, Silver and Gold layers, the analytics API and finally the dashboard. We also had to pick AWS or Azure, map at least eight cloud services, and explain why the design fits the bank's workload."

## The theory
"First, what is a C4 diagram? C4 is a way to draw software at four zoom levels: Context, Container, Component and Code. Level 2, the container level, shows the main running parts of a system, like APIs, databases and streams, and how they talk to each other. A 'container' here does not mean a Docker container. It just means any part that runs or stores data on its own.

Second, batch versus streaming. The old PayShield system uses batch: it copies data every four hours. That is why fraud checks are slow. Streaming means each payment is processed the moment it arrives, so the data is only seconds old.

Third, the lakehouse layers. Bronze keeps the raw data exactly as it arrived. Silver holds cleaned data. Gold holds the final business tables used for reports and the API."

## What we did
"We chose AWS. Then we designed two paths from one stream.

When a payment arrives, the Payment API puts it into Kinesis, which is AWS's streaming service.

The first path is the fast path. A Lambda function reads every event within about one second, checks it for fraud and writes the result to DynamoDB. So fraud analysts get data in one to two seconds, well under the 30-second target.

The second path is the slow path. The same events are saved in S3 as Bronze. AWS Glue, which runs Spark, cleans them into Silver and builds the star schema in Gold on Redshift. A small summary table goes to DynamoDB so the analytics API can answer in under 500 milliseconds. The dashboard uses QuickSight, and regulatory reports use Athena.

Because the old system cannot be switched off, AWS DMS copies its data into the same stream, so both systems can run side by side.

We mapped eleven capabilities to AWS services, including ECS and Lambda for compute, S3 for storage, Kinesis for streaming, IAM and Cognito for identity, Secrets Manager for secrets, CloudWatch for monitoring and Lake Formation for governance."

## Why it fits
"This design meets every requirement. Kinesis and Lambda scale automatically from 500 to 5,000 payments per second. S3 is cheap enough to keep seven years of history. Iceberg keeps old versions of tables, so old reports can be re-run. And DMS lets us migrate slowly without a big-bang switch.

In short, we replaced a slow four-hour batch system with a streaming system on AWS that is fast, scalable and keeps full history."
