# Task 1 - Architecture & Cloud Design

**Cloud chosen: AWS**

## C4 Level 2 Container Diagram

![C4 diagram](images/c4_diagram.png)

```mermaid
C4Container
    title PayShield - C4 Level 2 Container Diagram (AWS)

    Person(channels, "Payment Channels", "Cards, POS, mobile")
    System_Ext(onprem, "On-prem Payment App", "Old system, runs during migration")
    Person(business, "Business users and Regulators", "Dashboards and reports")
    Person(analyst, "Fraud Analyst", "Needs data in 30 s")

    System_Boundary(aws, "PayShield Data Platform on AWS") {
        Container(payapi, "Payment API", "API Gateway + ECS", "Receives payments")
        ContainerQueue(stream, "Event Stream", "Kinesis", "Carries payment events")
        Container(fraud, "Fraud Consumer", "Lambda", "Real-time fraud check")
        ContainerDb(fraudstore, "Fraud Store", "DynamoDB", "Latest risk data")
        Container(cdc, "CDC", "AWS DMS", "Copies on-prem data")
        ContainerDb(bronze, "Bronze", "S3", "Raw data")
        Container(etl, "ETL", "AWS Glue (Spark)", "Cleans and models data")
        ContainerDb(silver, "Silver", "S3 + Iceberg", "Clean data")
        ContainerDb(gold, "Gold", "Redshift", "Star schema")
        ContainerDb(summary, "Summary Store", "DynamoDB", "Fast API data")
        Container(anapi, "Analytics API", "API Gateway + Lambda", "Payment summary")
        Container(dashboard, "Dashboard", "QuickSight", "Charts and KPIs")
        Container(reg, "Regulatory Reporting", "Athena", "Reports")
    }

    Boundary(shared, "Shared services") {
        Container(iam, "Identity", "IAM + Cognito", "Login and roles")
        Container(secrets, "Secrets", "Secrets Manager", "Passwords and keys")
        Container(monitor, "Monitoring", "CloudWatch", "Logs and alarms")
        Container(gov, "Governance", "Lake Formation", "Data access control")
    }

    Rel(channels, payapi, "Payments")
    Rel(onprem, cdc, "Changes")
    Rel(payapi, stream, "Events")
    Rel(cdc, stream, "Events")
    Rel(stream, fraud, "Reads")
    Rel(fraud, fraudstore, "Writes")
    Rel(analyst, fraudstore, "Queries")
    Rel(stream, bronze, "Saves raw")
    Rel(etl, bronze, "Reads")
    Rel(etl, silver, "Writes")
    Rel(etl, gold, "Writes")
    Rel(gold, summary, "Exports")
    Rel(anapi, summary, "Reads")
    Rel(dashboard, anapi, "Calls")
    Rel(reg, gold, "SQL")
    Rel(business, dashboard, "Uses")
```

## AWS Services

| Capability | AWS Service |
|---|---|
| Compute | ECS Fargate, Lambda |
| Storage | S3 |
| Streaming | Kinesis Data Streams |
| Lakehouse | Glue, Iceberg, Athena |
| Warehouse | Redshift |
| API | API Gateway |
| Identity | IAM, Cognito |
| Secrets | Secrets Manager |
| Monitoring | CloudWatch |
| Governance | Lake Formation |

## Why this architecture fits

- **Speed:** payments go into Kinesis and the fraud Lambda reads them in about 1-2 seconds, well under 30 seconds.
- **Scale:** Kinesis, Lambda and ECS scale automatically from 500 to 5,000 transactions/sec.
- **History:** S3 is cheap for 7 years. Iceberg keeps old versions, so old reports can be re-run.
- **Fast API:** the API reads a small summary table in DynamoDB, so it answers in under 500 ms.
- **Safe migration:** DMS copies data from the old system, so both can run together.
