# Create a Step Functions State Machine

Lab Objective: Create a document processing workflow that evaluates the content of submitted documents (simulated as JSON input) and routes them through different processing steps based on their content.

1. Create a role for AWS Lambda
- Name: StepFunctionsRole
- Use case: Lambda
- Policy: AWSLambdaBasicExecutionRole

2. Upload the `lambda_function_code.zip` file to AWS CloudShell and unzip it
3. Create 5 Lambda functions using the latest Python run time and the following function names:

```InitialProcessingFunction``` - Parses the document and extracts information
```FinancialDocFunction``` - Processes financial documents
```HRDocFunction``` - Processes HR documents
```GenericDocFunction``` - Processes documents that are neither financial nor HR
```FinalizationFunction``` - Compiles results and optionally stores them in S3

You can use the following AWS CLI commands:

```bash
aws lambda create-function --function-name InitialProcessingFunction --runtime python3.9 --role <YOUR_ROLE_ARN> --handler initprocfunc.lambda_handler --zip-file fileb://initprocfunc.zip

aws lambda create-function --function-name FinancialDocFunction --runtime python3.9 --role <YOUR_ROLE_ARN> --handler findocfunc.lambda_handler --zip-file fileb://findocfunc.zip

aws lambda create-function --function-name HRDocFunction --runtime python3.9 --role <YOUR_ROLE_ARN> --handler hrdocfunc.lambda_handler --zip-file fileb://hrdocfunc.zip

aws lambda create-function --function-name GenericDocFunction --runtime python3.9 --role <YOUR_ROLE_ARN> --handler gendocfunc.lambda_handler --zip-file fileb://gendocfunc.zip

aws lambda create-function --function-name FinalizationFunction --runtime python3.9 --role <YOUR_ROLE_ARN> --handler finalizationfunc.lambda_handler --zip-file fileb://finalizationfunc.zip
```

4. Check the code from the "step-functions-lambda.md" file matches each function
5. Go to Step Functions and create a state machine
6. Update the ARNs of the functions in the "step-functions-state-machine.json" file
7. Allow Step Functions to create the IAM role with Lambda and X-Ray permissions
8. Import the JSON code from the "step-functions-state-machine.json" file
9. Run the following tests

## Testing

1. Navigate to your state machine in the AWS Step Functions console and click "Start execution"
2. Enter the following JSON input:

```json
{
  "docType": "Financial",
  "content": "This is a financial document."
}
```

3. Click "Start Execution" to initiate the workflow
4. Monitor the execution in the AWS Step Functions console. You can see which path the execution takes, inspect the input and output of each state
5. Repeat with different JSON input code to test different execution paths

```json
{
  "docType": "HR",
  "content": "This is a Human Resources document."
}
```

```json
{
  "docType": "Legal",
  "content": "This is a legal document."
}
```