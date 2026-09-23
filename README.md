# PayShield - Milestone 2

Case study: move PayShield Bank's payment data platform from on-prem to AWS.

| File | Task |
|---|---|
| [Task1_Architecture.md](Task1_Architecture.md) | C4 diagram and AWS services |
| [Task2_Data_Model.md](Task2_Data_Model.md) | Star schema, SCD Type 2, Data Vault |
| [Task3_Data_Engineering.md](Task3_Data_Engineering.md) | Bronze/Silver/Gold, data problems, Spark |
| [Task4_API.md](Task4_API.md) | OpenAPI, Pydantic model, Gherkin tests |
| [Task5_Migration.md](Task5_Migration.md) | Migration plan and rollback |
| [Task6_Security.md](Task6_Security.md) | Security fixes and DevSecOps pipeline |
| [Task7_ADR.md](Task7_ADR.md) | Architecture comparison and decision |
| [PayShield_Milestone2_Report.docx](PayShield_Milestone2_Report.docx) | All tasks in one Word document |

## Sample data and code

| Folder | What's inside |
|---|---|
| `data/` | 5 small CSV files (customers, merchant risk, payments, events, settlements) with the case-study problems in them |
| `code/pipeline.py` | Pandas Bronze → Silver → Gold: removes duplicates, orders events, finds late events, fixes double counting, merchant risk by date, monthly summary |
| `code/spark_job.py` | Spark version of the join with a broadcast join for merchant risk |
| `code/api.py` | FastAPI `GET /analytics/payment-summary` |

How to run:

```bash
pip install pandas fastapi uvicorn pyspark
python code/pipeline.py
python code/spark_job.py
cd code && uvicorn api:app --reload
```

