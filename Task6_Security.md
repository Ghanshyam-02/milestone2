# Task 6 - Security & DevSecOps

## Security weaknesses in the code

1. **SQL injection:** user input goes straight into the SQL. Input like `' OR '1'='1` returns all customers.
2. **No authentication:** anyone can call the API.
3. **No authorization:** any user can see any customer.
4. **Returns every column:** `SELECT *` also returns private data.
5. **No input validation:** `customer_id` can be anything.

## Fixed code

```python
@app.get("/customer/{customer_id}")
def get_customer(
    customer_id: str = Path(pattern=r"^C\d{4,10}$"),      # input validation
    user = Depends(get_current_user),                      # authentication
):
    if not user.can_view(customer_id):                     # authorization
        raise HTTPException(status_code=403)
    query = "SELECT customer_id, country, segment FROM customer WHERE customer_id = %s"
    return execute(query, (customer_id,))                  # parameterized SQL
```

## Security controls

| Control | What we do |
|---|---|
| Input validation | Check the format of every input. |
| Parameterized SQL | Never build SQL with string formatting. |
| Authentication | Login with tokens (Cognito). |
| Authorization / RBAC | Roles such as analyst and admin decide what each user can see. |
| Secrets management | Passwords are kept in AWS Secrets Manager, not in code. |
| PII protection | Return only needed columns, encrypt data, mask personal data. |
| Secure logging | Never log passwords, tokens or personal data. |

## DevSecOps pipeline

Developer Branch → Unit Tests → SAST → Secret Scan → SCA → Docker Build → Container Scan → DAST → Approval → Production

Low and medium issues only give a warning. These block the pipeline:

| Stage | Blocks the pipeline when |
|---|---|
| Unit tests | Any test fails |
| SAST | High or critical code issue (e.g. SQL injection) |
| Secret scan | Any password or key is found |
| SCA | Library has a high or critical vulnerability |
| Container scan | Image has a high or critical vulnerability |
| DAST | High-risk issue found in the running app |
| Approval | Not approved |
