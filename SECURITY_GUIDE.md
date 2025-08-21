# Smart Expense Analyzer - Security Guide

## Security Overview

The Smart Expense Analyzer implements comprehensive security measures across all layers of the application, following AWS Well-Architected Framework security principles and industry best practices.

## Security Architecture

### Defense in Depth Strategy
```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   PERIMETER     │    │   APPLICATION   │                │
│  │                 │    │                 │                │
│  │ • WAF Rules     │    │ • Input Valid.  │                │
│  │ • DDoS Protect  │    │ • Auth/Authz    │                │
│  │ • Rate Limiting │    │ • Session Mgmt  │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │     DATA        │    │   INFRASTRUCTURE│                │
│  │                 │    │                 │                │
│  │ • Encryption    │    │ • IAM Policies  │                │
│  │ • Access Control│    │ • VPC Security  │                │
│  │ • Data Privacy  │    │ • Monitoring    │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Identity and Access Management (IAM)

### IAM Roles and Policies

**Lambda Execution Role**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "textract:DetectDocumentText",
        "textract:AnalyzeDocument"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/ExpenseRecords"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::expense-analyzer-documents/*",
        "arn:aws:s3:::expense-analyzer-frontend/*"
      ]
    }
  ]
}
```

**API Gateway Resource Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:*:*:*/prod/*/*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": ["0.0.0.0/0"]
        }
      }
    }
  ]
}
```

### Least Privilege Principle
- Each service has minimal required permissions
- Regular audit of IAM policies and roles
- Temporary credentials for development access
- Service-specific roles with no cross-service access

## Data Protection

### Encryption at Rest

**S3 Bucket Encryption**:
```python
import boto3

def configure_s3_encryption():
    s3 = boto3.client('s3')
    
    # Enable default encryption
    s3.put_bucket_encryption(
        Bucket='expense-analyzer-documents',
        ServerSideEncryptionConfiguration={
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    },
                    'BucketKeyEnabled': True
                }
            ]
        }
    )
```

**DynamoDB Encryption**:
```python
def create_encrypted_table():
    dynamodb = boto3.client('dynamodb')
    
    table = dynamodb.create_table(
        TableName='ExpenseRecords',
        # ... other parameters
        SSESpecification={
            'Enabled': True,
            'SSEType': 'KMS',
            'KMSMasterKeyId': 'alias/aws/dynamodb'
        }
    )
```

### Encryption in Transit
- All API endpoints use HTTPS/TLS 1.2+
- S3 transfer encryption enabled
- Lambda-to-service communication encrypted
- Frontend-to-API communication over HTTPS only

### Data Classification and Handling

**Data Categories**:
- **Public**: Application documentation, public assets
- **Internal**: Application logs, metrics
- **Confidential**: Expense data, receipt images
- **Restricted**: User credentials, API keys

**Data Retention Policies**:
```python
def configure_data_retention():
    # S3 lifecycle policy
    lifecycle_config = {
        'Rules': [
            {
                'ID': 'ExpenseDocumentRetention',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'uploads/'},
                'Transitions': [
                    {
                        'Days': 30,
                        'StorageClass': 'STANDARD_IA'
                    },
                    {
                        'Days': 90,
                        'StorageClass': 'GLACIER'
                    }
                ],
                'Expiration': {'Days': 2555}  # 7 years
            }
        ]
    }
```

## Application Security

### Input Validation and Sanitization

**File Upload Validation**:
```python
import magic
from PIL import Image

def validate_uploaded_file(file_content, filename):
    """Comprehensive file validation"""
    
    # File type validation using magic numbers
    file_type = magic.from_buffer(file_content, mime=True)
    allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
    
    if file_type not in allowed_types:
        raise ValueError(f"Invalid file type: {file_type}")
    
    # File size validation
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_content) > max_size:
        raise ValueError("File size exceeds limit")
    
    # Image validation for image files
    if file_type.startswith('image/'):
        try:
            img = Image.open(io.BytesIO(file_content))
            img.verify()
        except Exception:
            raise ValueError("Invalid image file")
    
    # Filename sanitization
    safe_filename = secure_filename(filename)
    if not safe_filename:
        raise ValueError("Invalid filename")
    
    return True

def secure_filename(filename):
    """Sanitize filename to prevent path traversal"""
    import re
    import os
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename
```

**API Input Validation**:
```python
from marshmallow import Schema, fields, validate

class ExpenseSchema(Schema):
    amount = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    category = fields.Str(required=True, validate=validate.OneOf([
        'food', 'transport', 'office', 'healthcare', 'entertainment', 'utilities', 'other'
    ]))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    date = fields.Date(required=True)
    vendor = fields.Str(validate=validate.Length(max=200))

def validate_expense_data(data):
    schema = ExpenseSchema()
    try:
        result = schema.load(data)
        return result
    except ValidationError as err:
        raise ValueError(f"Validation error: {err.messages}")
```

### Cross-Site Scripting (XSS) Prevention

**Frontend Security Headers**:
```javascript
// Content Security Policy
const cspHeader = "default-src 'self'; " +
                 "script-src 'self' 'unsafe-inline'; " +
                 "style-src 'self' 'unsafe-inline'; " +
                 "img-src 'self' data: https:; " +
                 "connect-src 'self' https://*.amazonaws.com";

// Set security headers
document.querySelector('meta[http-equiv="Content-Security-Policy"]')
        .setAttribute('content', cspHeader);
```

**Output Encoding**:
```javascript
function sanitizeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function displayExpenseData(expense) {
    document.getElementById('vendor').textContent = sanitizeHTML(expense.vendor);
    document.getElementById('description').textContent = sanitizeHTML(expense.description);
}
```

### SQL Injection Prevention
- DynamoDB NoSQL database eliminates SQL injection risks
- Parameterized queries for any SQL operations
- Input validation before database operations

## Network Security

### API Gateway Security

**Rate Limiting Configuration**:
```python
def configure_api_throttling():
    apigateway = boto3.client('apigateway')
    
    # Create usage plan
    usage_plan = apigateway.create_usage_plan(
        name='ExpenseAnalyzerUsagePlan',
        description='Rate limiting for expense analyzer API',
        throttle={
            'rateLimit': 100.0,  # requests per second
            'burstLimit': 200    # burst capacity
        },
        quota={
            'limit': 10000,      # requests per period
            'period': 'DAY'      # DAY, WEEK, MONTH
        }
    )
```

**CORS Configuration**:
```python
def configure_cors():
    return {
        'Access-Control-Allow-Origin': '*',  # Configure specific domains in production
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Max-Age': '3600'
    }
```

### VPC Security (Optional Enhancement)

**VPC Configuration for Enhanced Security**:
```python
def create_vpc_configuration():
    ec2 = boto3.client('ec2')
    
    # Create VPC
    vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc['Vpc']['VpcId']
    
    # Create private subnets for Lambda
    private_subnet = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock='10.0.1.0/24',
        AvailabilityZone='us-east-1a'
    )
    
    # Create VPC endpoints for AWS services
    vpc_endpoints = [
        {'service': 'com.amazonaws.us-east-1.s3', 'type': 'Gateway'},
        {'service': 'com.amazonaws.us-east-1.dynamodb', 'type': 'Gateway'},
        {'service': 'com.amazonaws.us-east-1.textract', 'type': 'Interface'}
    ]
    
    for endpoint in vpc_endpoints:
        ec2.create_vpc_endpoint(
            VpcId=vpc_id,
            ServiceName=endpoint['service'],
            VpcEndpointType=endpoint['type']
        )
```

## Monitoring and Incident Response

### Security Monitoring

**CloudTrail Configuration**:
```python
def configure_cloudtrail():
    cloudtrail = boto3.client('cloudtrail')
    
    trail = cloudtrail.create_trail(
        Name='ExpenseAnalyzerAuditTrail',
        S3BucketName='expense-analyzer-audit-logs',
        IncludeGlobalServiceEvents=True,
        IsMultiRegionTrail=True,
        EnableLogFileValidation=True,
        EventSelectors=[
            {
                'ReadWriteType': 'All',
                'IncludeManagementEvents': True,
                'DataResources': [
                    {
                        'Type': 'AWS::S3::Object',
                        'Values': ['arn:aws:s3:::expense-analyzer-documents/*']
                    },
                    {
                        'Type': 'AWS::DynamoDB::Table',
                        'Values': ['arn:aws:dynamodb:*:*:table/ExpenseRecords']
                    }
                ]
            }
        ]
    )
```

**CloudWatch Security Alarms**:
```python
def create_security_alarms():
    cloudwatch = boto3.client('cloudwatch')
    
    # Failed authentication attempts
    cloudwatch.put_metric_alarm(
        AlarmName='HighFailedAuthAttempts',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='4XXError',
        Namespace='AWS/ApiGateway',
        Period=300,
        Statistic='Sum',
        Threshold=50.0,
        ActionsEnabled=True,
        AlarmActions=[
            'arn:aws:sns:us-east-1:123456789012:security-alerts'
        ],
        AlarmDescription='High number of failed authentication attempts'
    )
    
    # Unusual data access patterns
    cloudwatch.put_metric_alarm(
        AlarmName='UnusualDataAccess',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='ConsumedReadCapacityUnits',
        Namespace='AWS/DynamoDB',
        Period=300,
        Statistic='Sum',
        Threshold=1000.0,
        AlarmDescription='Unusual data access pattern detected'
    )
```

### Incident Response Plan

**Security Incident Classification**:
- **P1 - Critical**: Data breach, system compromise
- **P2 - High**: Unauthorized access, service disruption
- **P3 - Medium**: Security policy violation, suspicious activity
- **P4 - Low**: Security configuration issue, minor vulnerability

**Response Procedures**:
1. **Detection and Analysis**
   - Monitor CloudWatch alarms and logs
   - Analyze security events and patterns
   - Determine incident severity and scope

2. **Containment and Eradication**
   - Isolate affected systems
   - Revoke compromised credentials
   - Apply security patches and fixes

3. **Recovery and Post-Incident**
   - Restore services from clean backups
   - Implement additional security measures
   - Document lessons learned

## Compliance and Governance

### GDPR Compliance

**Data Subject Rights Implementation**:
```python
def handle_data_subject_request(user_id, request_type):
    """Handle GDPR data subject requests"""
    
    if request_type == 'access':
        # Right to access - export user data
        return export_user_data(user_id)
    
    elif request_type == 'rectification':
        # Right to rectification - update incorrect data
        return update_user_data(user_id)
    
    elif request_type == 'erasure':
        # Right to erasure - delete user data
        return delete_user_data(user_id)
    
    elif request_type == 'portability':
        # Right to data portability - export in machine-readable format
        return export_user_data_portable(user_id)

def delete_user_data(user_id):
    """Securely delete all user data"""
    
    # Delete from DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ExpenseRecords')
    
    # Query and delete user expenses
    response = table.query(
        IndexName='UserIndex',
        KeyConditionExpression=Key('user_id').eq(user_id)
    )
    
    for item in response['Items']:
        table.delete_item(Key={'expense_id': item['expense_id']})
    
    # Delete from S3
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(
        Bucket='expense-analyzer-documents',
        Prefix=f'users/{user_id}/'
    )
    
    if 'Contents' in objects:
        delete_keys = [{'Key': obj['Key']} for obj in objects['Contents']]
        s3.delete_objects(
            Bucket='expense-analyzer-documents',
            Delete={'Objects': delete_keys}
        )
```

### SOC 2 Compliance

**Control Implementation**:
- **Security**: Multi-layered security controls
- **Availability**: High availability architecture
- **Processing Integrity**: Data validation and error handling
- **Confidentiality**: Encryption and access controls
- **Privacy**: GDPR compliance and data protection

### Regular Security Assessments

**Automated Security Scanning**:
```python
def run_security_scan():
    """Automated security assessment"""
    
    # Check for security misconfigurations
    config = boto3.client('config')
    
    # Evaluate compliance rules
    rules = [
        's3-bucket-public-access-prohibited',
        'dynamodb-table-encrypted-kms',
        'lambda-function-public-access-prohibited',
        'api-gw-associated-with-waf'
    ]
    
    for rule in rules:
        response = config.get_compliance_details_by_config_rule(
            ConfigRuleName=rule
        )
        
        if response['ComplianceDetails']['ComplianceType'] != 'COMPLIANT':
            # Send alert for non-compliant resources
            send_security_alert(rule, response)
```

## Security Best Practices Checklist

### Development Security
- [ ] Input validation on all user inputs
- [ ] Output encoding to prevent XSS
- [ ] Secure coding practices followed
- [ ] Dependencies regularly updated
- [ ] Security testing in CI/CD pipeline

### Infrastructure Security
- [ ] IAM roles follow least privilege principle
- [ ] All data encrypted at rest and in transit
- [ ] Network security groups properly configured
- [ ] Regular security patches applied
- [ ] Monitoring and alerting configured

### Operational Security
- [ ] Regular security assessments conducted
- [ ] Incident response plan tested
- [ ] Security training for development team
- [ ] Compliance requirements met
- [ ] Backup and recovery procedures tested

### Data Protection
- [ ] Data classification implemented
- [ ] Retention policies configured
- [ ] GDPR compliance measures in place
- [ ] Data access logging enabled
- [ ] Secure data disposal procedures

## Security Contact Information

**Security Team**: security@expense-analyzer.com
**Incident Reporting**: incidents@expense-analyzer.com
**Vulnerability Disclosure**: security-reports@expense-analyzer.com

**Response Times**:
- Critical incidents: 1 hour
- High priority: 4 hours
- Medium priority: 24 hours
- Low priority: 72 hours