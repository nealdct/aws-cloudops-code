## Function Code

### InitialProcessingFunction

```python
import json

def lambda_handler(event, context):
    # Simulate extracting information from the document
    doc_type = event.get('docType', 'generic')
    return {
        'statusCode': 200,
        'body': json.dumps(f'Initial processing complete. Document type: {doc_type}'),
        'docType': doc_type
    }
```

### FinancialDocFunction

```python
import json

def lambda_handler(event, context):
    # Simulate processing specific to the document type
    return {
        'statusCode': 200,
        'body': json.dumps('Processed a financial document.'),
    }
```

### HRDocFunction

```python
import json

def lambda_handler(event, context):
    # Simulate processing specific to the document type
    return {
        'statusCode': 200,
        'body': json.dumps('Processed a HR document.'),
    }
```

### GenericDocFunction

```python
import json

def lambda_handler(event, context):
    # Simulate processing specific to the document type
    return {
        'statusCode': 200,
        'body': json.dumps('Processed a generic document.'),
    }
```

### FinalizationFunction

```python
import json

def lambda_handler(event, context):
    # Simulate finalizing the document processing
    return {
        'statusCode': 200,
        'body': json.dumps('Finalization complete. Document processed.'),
    }
```

