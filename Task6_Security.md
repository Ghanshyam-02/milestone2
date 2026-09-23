# Task 6 - Security & DevSecOps

## What was asked

- Find the security weaknesses in the given API code.
- Propose secure coding controls: input validation, parameterized SQL, authentication, authorization, RBAC, secrets management, PII protection, secure logging.
- Design a DevSecOps pipeline and say which failures should block it.

## The given code

```python
@app.get("/customer/{customer_id}")
def get_customer(customer_id):
    query = f"""
    SELECT *
    FROM customer
    WHERE customer_id = '{customer_id}'
    """
    return execute(query)
```

## Security weaknesses

| # | Weakness | Why it is dangerous |
|---|---|---|
| 1 | **SQL injection** | User input goes straight into the SQL. Input like `' OR '1'='1` makes the query return **all** customers. |
| 2 | **No authentication** | Anyone can call the API without logging in. |
| 3 | **No authorization** | Any user can see any customer by changing the ID in the URL. |
| 4 | **Returns every column** | `SELECT *` also returns private data the caller does not need. |
| 5 | **No input validation** | `customer_id` can be any text of any length. |
| 6 | **Errors shown to user** | Database errors can reveal table names to attackers. |

**How the attack works:** with input `' OR '1'='1` the query becomes

```sql
SELECT * FROM customer WHERE customer_id = '' OR '1'='1'
```

`'1'='1'` is always true, so every customer is returned.

## Fixed code

```python
@app.get("/customer/{customer_id}")
def get_customer(
    customer_id: str = Path(pattern=r"^C\d{4,10}$"),      # 1. input validation
    user = Depends(get_current_user),                      # 2. authentication
):
    if not user.can_view(customer_id):                     # 3. authorization
        raise HTTPException(status_code=403)
    query = "SELECT customer_id, country, segment FROM customer WHERE customer_id = %s"
    return execute(query, (customer_id,))                  # 4. parameterized SQL, only needed columns
```

With a **parameterized query**, the input is sent separately from the SQL, so it can never become SQL code.

## Security controls

| Control | What we do |
|---|---|
| Input validation | Check the format of every input (e.g. `C` + digits). Reject anything else with 400. |
| Parameterized SQL | Never build SQL with string formatting. Always use `%s` / `?` placeholders. |
| Authentication | Users log in and get a token (AWS Cognito). No token = 401. |
| Authorization | Check the user is allowed to see this customer. Not allowed = 403. |
| RBAC (role-based access) | Roles like `fraud_analyst`, `support_agent`, `admin` decide what each user can see. |
| Secrets management | Database passwords are stored in AWS Secrets Manager, never in the code. |
| PII protection | Return only needed columns, encrypt data, mask personal data (e.g. `C0**01`). |
| Secure logging | Log who accessed what, but never log passwords, tokens or personal data. |

## DevSecOps pipeline

Developer Branch → Unit Tests → SAST → Secret Scan → SCA → Docker Build → Container Scan → DAST → Approval → Production

| Stage | What it checks | Example tool | Blocks the pipeline when |
|---|---|---|---|
| Unit tests | Code works correctly | pytest | Any test fails |
| SAST | Source code for security bugs | SonarQube, Bandit | High or critical issue (e.g. SQL injection) |
| Secret scan | Passwords or keys in the code | Gitleaks | Any secret is found |
| SCA | Libraries we use | pip-audit, Snyk | High or critical vulnerability |
| Docker build | Builds the app image | Docker | Build fails |
| Container scan | The Docker image | Trivy | High or critical vulnerability |
| DAST | The running app, tested from outside | OWASP ZAP | High-risk issue found |
| Approval | A person checks the release | Manual | Not approved |

Low and medium issues only give a warning and a ticket, so the pipeline is not blocked for small problems.
