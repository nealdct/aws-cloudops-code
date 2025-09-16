# Create a Lambda function with Python and the below code

```python
def lambda_handler(event, context):
    message = event.get('message')
    print(message)
```

# Create an Eventbridge schedule with the following payload

```json
{
  "message": "Hello from EventBridge!"
}
```
