# Script - Task 6: Security & DevSecOps

## What was asked
"In Task 6, we were given a small piece of API code that reads a customer from the database. We had to find its security weaknesses, propose secure coding controls, and design a DevSecOps pipeline, saying which failures should stop a release."

## The theory
"The biggest problem here is SQL injection. It happens when user input is pasted directly into a SQL query. An attacker can then type SQL code instead of a normal value and change what the query does. The fix is a parameterized query, where the input is sent separately from the SQL, so it can never become code.

Two other key ideas are authentication and authorization. Authentication asks 'who are you?', which is the login. Authorization asks 'are you allowed to see this?'. RBAC, or role-based access control, gives permissions to roles like analyst or admin instead of to each person.

DevSecOps means adding security checks into the automatic build and release pipeline, so problems are caught early. SAST scans our source code. A secret scan looks for passwords left in the code. SCA checks the third-party libraries we use. A container scan checks the Docker image. DAST attacks the running application from the outside, like a real hacker would."

## What we did
"We found these weaknesses in the code.

First, SQL injection. If someone enters ' OR '1'='1, the query becomes WHERE customer_id = '' OR '1'='1'. That is always true, so it returns every customer in the bank.

Second, there is no authentication, so anyone can call the API. Third, there is no authorization, so any user can see any customer. Fourth, SELECT star returns every column, including private data. Fifth, there is no input validation.

We fixed the code in four ways. We check that the customer ID matches the pattern C followed by digits. We require a login token. We check that the user is allowed to see that customer. And we use a parameterized query that returns only the columns needed.

We also listed the other controls: passwords go in AWS Secrets Manager and never in the code, personal data is encrypted and masked, and logs never contain passwords, tokens or personal data.

Our pipeline runs in this order: unit tests, SAST, secret scan, SCA, Docker build, container scan, DAST, then manual approval before production. The pipeline stops if any test fails, if any secret is found, if any high or critical vulnerability is found, or if the release is not approved. Low and medium issues only raise a warning and a ticket, so developers are not blocked by small problems and don't try to skip the pipeline."
