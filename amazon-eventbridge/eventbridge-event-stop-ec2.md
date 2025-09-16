# Launch instance, stop instance
1. Launch an EC2 instance
aws ec2 run-instances --image-id ami-00ca32bbc84273381 --instance-type t2.micro --placement AvailabilityZone=us-east-1a
2. Stop the EC2 instance
aws ec2 stop-instances --instance-id i-XXXXXXXXXXXXXXX
3. Terminate the EC2 instance
aws ec2 terminate-instances --instance-id i-XXXXXXXXXXXXXXX

## Python code for function
```python
import json

def lambda_handler(event, context):
    print('LogEC2StopInstance')
    print('Received event:', json.dumps(event, indent=2))
    return {
        'statusCode': 200,
        'body': 'Finished'
    }
```