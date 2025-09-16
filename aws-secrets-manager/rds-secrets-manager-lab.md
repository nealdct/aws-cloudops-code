# Create the DB

1. Create an RDS DB using MySQL.

2. Call the DB sampledb and same for table name

3. Make it publily available.

4. Ensure security group rule allows 3306 from anywhere.

# Create the secret

1. In Secrets Manager create "Credentials for Amazon RDS database".

2. Set the credentials.

3. Select the DB.

4. Make sure the name is prod/sampledb

# Build the layer package (in CloudShell)

```bash
mkdir python
pip install pymysql -t python/
zip -r pymysql-layer.zip python
```

# Create the Layer in AWS Console

1. Go to AWS Lambda Console > Layers > Create layer.

2. Name it (e.g., PyMySQL).

3. Upload pymysql-layer.zip.

4. Select the runtime(s) you use (Python 3.9, 3.11, etc.).

5. Click Create.

# Create the function

1. Use the Python runtime.

2. Add the code from `rds-secrets-manager-lab.py`

3. Add the PyMySQL layer.

4. Create an environment variable:

SECRET_NAME=prod/sampledb

# Run a test event

1. In AWS Lambda run a test event with the following code.

{ "item": "hello-from-lambda", "limit": 10 }

2. Rerun the test event, modifying the text and check results.

