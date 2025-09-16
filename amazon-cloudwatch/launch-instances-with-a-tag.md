# Launch instances with a tag
aws ec2 run-instances --image-id ami-00ca32bbc84273381 --count 2 --instance-type t2.micro --tag-specifications 'ResourceType=instance,Tags=[{Key=Department,Value=Operations}]'

# CloudWatch Logs Insights query
fields @timestamp, @message | sort @timestamp desc | limit 25
