# Smart Expense Analyzer - Troubleshooting Guide

## Common Issues and Solutions

### Deployment Issues

#### 1. AWS Permissions Errors

**Problem**: `AccessDenied` or `UnauthorizedOperation` errors during deployment

**Symptoms**:
```
botocore.exceptions.ClientError: An error occurred (AccessDenied) when calling the CreateBucket operation
```

**Solutions**:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify required permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/username \
  --action-names s3:CreateBucket dynamodb:CreateTable lambda:CreateFunction \
  --resource-arns "*"

# Update IAM policy with required permissions
aws iam attach-user-policy \
  --user-name username \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
```

**Prevention**:
- Use deployment scripts that check permissions first
- Implement least-privilege IAM policies
- Test deployments in development environment

#### 2. Resource Already Exists Errors

**Problem**: `BucketAlreadyOwnedByYou` or `ResourceInUseException` errors

**Symptoms**:
```
An error occurred (BucketAlreadyOwnedByYou) when calling the CreateBucket operation
```

**Solutions**:
```python
# Handle existing resources gracefully
def create_s3_bucket_safe(bucket_name):
    s3 = boto3.client('s3')
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Created bucket: {bucket_name}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {bucket_name} already exists")
        else:
            print(f"Error creating bucket: {e}")
            raise

# Check resource existence before creation
def resource_exists(resource_type, resource_name):
    if resource_type == 's3':
        s3 = boto3.client('s3')
        try:
            s3.head_bucket(Bucket=resource_name)
            return True
        except ClientError:
            return False
```

#### 3. Lambda Deployment Failures

**Problem**: Lambda function creation or update fails

**Symptoms**:
```
An error occurred (InvalidParameterValueException) when calling the CreateFunction operation
```

**Solutions**:
```python
# Check Lambda package size
import os
def check_lambda_package_size(zip_file_path):
    size_mb = os.path.getsize(zip_file_path) / (1024 * 1024)
    if size_mb > 50:  # 50MB limit for direct upload
        print(f"Package too large ({size_mb:.1f}MB). Use S3 upload method.")
        return False
    return True

# Use S3 for large packages
def deploy_large_lambda(function_name, zip_file_path):
    s3 = boto3.client('s3')
    lambda_client = boto3.client('lambda')
    
    # Upload to S3 first
    bucket = 'lambda-deployment-bucket'
    key = f'{function_name}.zip'
    s3.upload_file(zip_file_path, bucket, key)
    
    # Create/update function from S3
    lambda_client.create_function(
        FunctionName=function_name,
        Code={'S3Bucket': bucket, 'S3Key': key},
        # ... other parameters
    )
```

### Runtime Issues

#### 4. Lambda Function Timeouts

**Problem**: Lambda functions timing out during execution

**Symptoms**:
```
Task timed out after 30.00 seconds
```

**Solutions**:
```python
# Increase timeout in deployment script
lambda_client.update_function_configuration(
    FunctionName='process_document',
    Timeout=300,  # 5 minutes
    MemorySize=1024  # Increase memory for better performance
)

# Optimize function code
def process_document_optimized(event, context):
    # Check remaining time
    remaining_time = context.get_remaining_time_in_millis()
    if remaining_time < 30000:  # Less than 30 seconds
        return {'statusCode': 202, 'body': 'Processing queued for retry'}
    
    # Process in chunks for large documents
    # ... implementation
```

**Monitoring**:
```python
# Add CloudWatch metrics
import boto3
cloudwatch = boto3.client('cloudwatch')

def put_custom_metric(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='ExpenseAnalyzer',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }
        ]
    )
```

#### 5. DynamoDB Throttling

**Problem**: DynamoDB read/write capacity exceeded

**Symptoms**:
```
ProvisionedThroughputExceededException: The level of configured provisioned throughput for the table was exceeded
```

**Solutions**:
```python
# Implement exponential backoff
import time
import random
from botocore.exceptions import ClientError

def dynamodb_put_with_retry(table, item, max_retries=3):
    for attempt in range(max_retries):
        try:
            table.put_item(Item=item)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ProvisionedThroughputExceededException':
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                    continue
            raise
    return False

# Switch to on-demand billing
def configure_on_demand_billing():
    dynamodb = boto3.client('dynamodb')
    dynamodb.modify_table(
        TableName='ExpenseRecords',
        BillingMode='PAY_PER_REQUEST'
    )
```

#### 6. S3 Access Denied Errors

**Problem**: Cannot access S3 objects or bucket

**Symptoms**:
```
An error occurred (AccessDenied) when calling the GetObject operation
```

**Solutions**:
```python
# Check and fix bucket policy
def fix_s3_bucket_policy(bucket_name):
    s3 = boto3.client('s3')
    
    # Disable block public access for frontend bucket
    if 'frontend' in bucket_name:
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
    
    # Set appropriate bucket policy
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }
    
    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )
```

### Application Issues

#### 7. OCR Processing Failures

**Problem**: Textract fails to extract text from documents

**Symptoms**:
```
InvalidS3ObjectException: Unable to get object metadata from S3
```

**Solutions**:
```python
# Validate file before processing
def validate_document_for_ocr(s3_bucket, s3_key):
    s3 = boto3.client('s3')
    
    try:
        # Check if object exists
        response = s3.head_object(Bucket=s3_bucket, Key=s3_key)
        
        # Check file size (Textract limits)
        file_size = response['ContentLength']
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError("File too large for Textract processing")
        
        # Check content type
        content_type = response.get('ContentType', '')
        allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
        if content_type not in allowed_types:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            raise ValueError("File not found in S3")
        raise

# Implement fallback processing
def process_document_with_fallback(s3_bucket, s3_key):
    textract = boto3.client('textract')
    
    try:
        # Try synchronous processing first
        response = textract.detect_document_text(
            Document={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}}
        )
        return extract_text_from_response(response)
    
    except ClientError as e:
        if 'UnsupportedDocumentException' in str(e):
            # Try asynchronous processing for complex documents
            return start_async_text_detection(s3_bucket, s3_key)
        raise
```

#### 8. Frontend Loading Issues

**Problem**: Frontend website not loading or displaying errors

**Symptoms**:
- Blank page or 404 errors
- CORS errors in browser console
- API calls failing

**Solutions**:
```javascript
// Check API endpoint configuration
const API_BASE_URL = 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod';

// Test API connectivity
async function testAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/expenses`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        console.log('API connection successful');
        return true;
    } catch (error) {
        console.error('API connection failed:', error);
        return false;
    }
}

// Handle CORS issues
function setupAPIClient() {
    // Ensure proper headers are set
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };
    
    // Add error handling for network issues
    window.addEventListener('unhandledrejection', event => {
        if (event.reason.name === 'TypeError' && event.reason.message.includes('fetch')) {
            console.error('Network error - check API endpoint configuration');
            showErrorMessage('Unable to connect to server. Please try again later.');
        }
    });
}
```

#### 9. File Upload Failures

**Problem**: File uploads failing or timing out

**Symptoms**:
```
Request failed with status code 413 (Payload Too Large)
Request timeout
```

**Solutions**:
```javascript
// Implement file size validation
function validateFile(file) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    
    if (file.size > maxSize) {
        throw new Error('File size exceeds 10MB limit');
    }
    
    if (!allowedTypes.includes(file.type)) {
        throw new Error('Unsupported file type. Please use JPEG, PNG, or PDF.');
    }
    
    return true;
}

// Implement retry logic
async function uploadFileWithRetry(file, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: 'POST',
                body: formData,
                timeout: 30000 // 30 second timeout
            });
            
            if (response.ok) {
                return await response.json();
            }
            
            throw new Error(`Upload failed: ${response.statusText}`);
        } catch (error) {
            if (attempt === maxRetries) {
                throw error;
            }
            
            // Wait before retry
            await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
    }
}
```

### Performance Issues

#### 10. Slow Dashboard Loading

**Problem**: Dashboard takes too long to load expense data

**Solutions**:
```javascript
// Implement pagination
async function loadExpenses(page = 1, limit = 20) {
    const response = await fetch(
        `${API_BASE_URL}/expenses?page=${page}&limit=${limit}`
    );
    return response.json();
}

// Add loading indicators
function showLoadingSpinner() {
    document.getElementById('loading-spinner').style.display = 'block';
}

function hideLoadingSpinner() {
    document.getElementById('loading-spinner').style.display = 'none';
}

// Implement caching
class ExpenseCache {
    constructor() {
        this.cache = new Map();
        this.ttl = 5 * 60 * 1000; // 5 minutes
    }
    
    get(key) {
        const item = this.cache.get(key);
        if (item && Date.now() - item.timestamp < this.ttl) {
            return item.data;
        }
        this.cache.delete(key);
        return null;
    }
    
    set(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }
}
```

## Diagnostic Tools and Commands

### AWS CLI Diagnostics

```bash
# Check AWS configuration
aws configure list
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://expense-analyzer-documents/
aws s3 cp test-file.txt s3://expense-analyzer-documents/

# Check Lambda function status
aws lambda get-function --function-name process_document
aws lambda invoke --function-name process_document output.json

# Check DynamoDB table
aws dynamodb describe-table --table-name ExpenseRecords
aws dynamodb scan --table-name ExpenseRecords --limit 5

# Check API Gateway
aws apigateway get-rest-apis
aws apigateway test-invoke-method \
  --rest-api-id your-api-id \
  --resource-id resource-id \
  --http-method GET
```

### CloudWatch Logs Analysis

```bash
# View Lambda function logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/process_document"
aws logs get-log-events \
  --log-group-name "/aws/lambda/process_document" \
  --log-stream-name "2024/01/15/[$LATEST]abc123"

# Search for errors
aws logs filter-log-events \
  --log-group-name "/aws/lambda/process_document" \
  --filter-pattern "ERROR"
```

### Health Check Scripts

```python
#!/usr/bin/env python3
"""Health check script for Smart Expense Analyzer"""

import boto3
import requests
import json
from datetime import datetime

def check_s3_buckets():
    """Check S3 bucket accessibility"""
    s3 = boto3.client('s3')
    buckets = ['expense-analyzer-documents', 'expense-analyzer-frontend']
    
    for bucket in buckets:
        try:
            s3.head_bucket(Bucket=bucket)
            print(f"✓ S3 bucket {bucket} is accessible")
        except Exception as e:
            print(f"✗ S3 bucket {bucket} error: {e}")
            return False
    return True

def check_dynamodb_table():
    """Check DynamoDB table status"""
    dynamodb = boto3.client('dynamodb')
    
    try:
        response = dynamodb.describe_table(TableName='ExpenseRecords')
        status = response['Table']['TableStatus']
        print(f"✓ DynamoDB table status: {status}")
        return status == 'ACTIVE'
    except Exception as e:
        print(f"✗ DynamoDB table error: {e}")
        return False

def check_lambda_functions():
    """Check Lambda function status"""
    lambda_client = boto3.client('lambda')
    functions = ['process_document', 'get_expenses', 'upload_api']
    
    for func_name in functions:
        try:
            response = lambda_client.get_function(FunctionName=func_name)
            state = response['Configuration']['State']
            print(f"✓ Lambda function {func_name}: {state}")
        except Exception as e:
            print(f"✗ Lambda function {func_name} error: {e}")
            return False
    return True

def check_api_endpoints():
    """Check API Gateway endpoints"""
    # Get API Gateway URL from environment or configuration
    api_base_url = "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"
    
    try:
        response = requests.get(f"{api_base_url}/expenses", timeout=10)
        if response.status_code == 200:
            print("✓ API Gateway endpoints are responding")
            return True
        else:
            print(f"✗ API Gateway returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API Gateway error: {e}")
        return False

def main():
    """Run all health checks"""
    print("Smart Expense Analyzer - Health Check")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    checks = [
        ("S3 Buckets", check_s3_buckets),
        ("DynamoDB Table", check_dynamodb_table),
        ("Lambda Functions", check_lambda_functions),
        ("API Endpoints", check_api_endpoints)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"Checking {check_name}...")
        result = check_func()
        results.append((check_name, result))
        print()
    
    # Summary
    print("Health Check Summary:")
    print("-" * 20)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{check_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("✓ All systems operational")
        return 0
    else:
        print("✗ Some systems need attention")
        return 1

if __name__ == "__main__":
    exit(main())
```

## Getting Help

### Self-Service Resources
1. Check this troubleshooting guide
2. Review application logs in CloudWatch
3. Run the health check script
4. Check AWS service status page

### Support Channels
- **Documentation**: Review all documentation files
- **GitHub Issues**: Report bugs and request features
- **Community Forum**: Ask questions and share solutions
- **Email Support**: technical-support@expense-analyzer.com

### When Reporting Issues
Include the following information:
1. Error messages (exact text)
2. Steps to reproduce the issue
3. Environment details (AWS region, browser, etc.)
4. Screenshots or logs
5. Expected vs. actual behavior

### Emergency Contacts
- **Critical Issues**: emergency@expense-analyzer.com
- **Security Issues**: security@expense-analyzer.com
- **Response Time**: Within 2 hours for critical issues