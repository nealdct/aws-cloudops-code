```bash
#!/bin/bash
yum update -y
yum install -y httpd
systemctl enable httpd
systemctl start httpd
aws s3 cp s3://YOUR-BUCKET-NAME/index.html /var/www/html/index.html
```
