
## Create a security group

aws ec2 create-security-group --group-name ALB-EC2-Access --description "ASG ALB CLI Lab" --region us-east-1

aws ec2 authorize-security-group-ingress --group-name ALB-EC2-Access --protocol tcp --port 22 --cidr 0.0.0.0/0 --region us-east-1

aws ec2 authorize-security-group-ingress --group-name ALB-EC2-Access --protocol tcp --port 80 --cidr 0.0.0.0/0 --region us-east-1

## create auto scaling group

1. Create a file in CloudShell named userdata.sh with the following contents:

#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

EC2AZ=$(TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"` && curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/placement/availability-zone)

echo '<center><h1>This Amazon EC2 instance is located in Availability Zone: AZID </h1></center>' > /var/www/html/index.txt
sed "s/AZID/$EC2AZ/" /var/www/html/index.txt > /var/www/html/index.html

2. Based64 encode the script

USERDATA=$(base64 -w 0 userdata.sh)

3. Get the latest AMI ID

aws ssm get-parameters \
  --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query "Parameters[0].Value" \
  --output text

4. Create the launch template

aws ec2 create-launch-template \
  --launch-template-name LT1 \
  --version-description "Amazon Linux 2023 with httpd and AZ web page" \
  --launch-template-data "{
    \"ImageId\": \"<AMI_ID>\",
    \"InstanceType\": \"t2.micro\",
    \"SecurityGroupIds\": [\"<SECURITY_GROUP_ID>\"],
    \"UserData\": \"${USERDATA}\",
    \"TagSpecifications\": [
      {
        \"ResourceType\": \"instance\",
        \"Tags\": [
          {\"Key\": \"Name\", \"Value\": \"asg-alb-cli-lab\"}
        ]
      }
    ]
  }"


5. Get the ID of the default VPC

aws ec2 describe-vpcs \
  --filters "Name=isDefault,Values=true" \
  --query "Vpcs[0].VpcId" \
  --output text

6. Get the subnet IDs for us-east-1a and us-east-1b (replace default VPC ID)

aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=<VPC_ID>" "Name=availability-zone,Values=us-east-1a,us-east-1b" \
  --query "Subnets[*].{SubnetId:SubnetId,AZ:AvailabilityZone}" \
  --output table


7. Create the ASG

aws autoscaling create-auto-scaling-group --auto-scaling-group-name ASG1 --launch-template "LaunchTemplateName=LT1" --min-size 1 --max-size 3 --desired-capacity 2 --availability-zones "us-east-1a" "us-east-1b" --vpc-zone-identifier "<SUBNET-ID-1>, <SUBNET-ID-2>"

## create target group, load balancer, listener, and then link it all up

aws elbv2 create-target-group --name TG1 --protocol HTTP --port 80 --vpc-id <VPC-ID>

aws elbv2 create-load-balancer --name ALB1 --subnets <SUBNET-ID-1> <SUBNET-ID-2> --security-groups <SECURITY-GROUP-ID>

aws elbv2 create-listener --load-balancer-arn <ALB-ARN> --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=<TARGET-GROUP-ARN>

aws autoscaling attach-load-balancer-target-groups --auto-scaling-group-name ASG1 --target-group-arns <TARGET-GROUP-ARN>

## delete ASG and ALB

aws elbv2 delete-load-balancer --load-balancer-arn <ALB-ARN>

aws autoscaling delete-auto-scaling-group --auto-scaling-group-name ASG1 --force-delete