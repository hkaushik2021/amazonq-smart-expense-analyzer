# Smart Expense Analyzer - Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the Smart Expense Analyzer application to AWS.

## Prerequisites
- AWS CLI configured with appropriate permissions
- Python 3.8 or higher
- boto3 library installed
- Valid AWS account with billing enabled

## Required AWS Permissions
Your AWS user/role needs the following permissions:
- S3: CreateBucket, PutObject, PutBucketPolicy, PutPublicAccessBlock
- DynamoDB: CreateTable, PutItem, GetItem, Scan
- Lambda: CreateFunction, UpdateFunctionCode, AddPermission
- IAM: CreateRole, AttachRolePolicy, PutRolePolicy
- API Gateway: CreateRestApi, CreateResource, CreateMethod
- Textract: DetectDocumentText, AnalyzeDocument

## Deployment Steps

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd smart-expense-analyzer

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure
```

### 2. Infrastructure Deployment
```bash
# Deploy AWS infrastructure
python deploy-infrastructure.py
```

This script creates:
- S3 buckets for documents and frontend
- DynamoDB table for expense records
- IAM roles and policies
- API Gateway configuration

### 3. Lambda Functions Deployment
```bash
# Deploy Lambda functions
python deploy-lambdas.py
```

This script deploys:
- process_document function (OCR processing)
- get_expenses function (data retrieval)
- upload_api function (file upload handling)

### 4. Frontend Deployment
```bash
# Generate and deploy frontend
python generate_static_html.py
```

This deploys both:
- `frontend/index.html` - Main dashboard
- `frontend/upload-receipt.html` - File upload page

### 5. Deployment Verification
```bash
# Run comprehensive tests
python test_deployment.py
```

## Environment-Specific Configurations

### Development Environment
- Use smaller DynamoDB capacity units
- Enable detailed CloudWatch logging
- Use development S3 bucket names

### Production Environment
- Enable S3 versioning and lifecycle policies
- Configure CloudFront for global distribution
- Set up monitoring and alerting
- Enable backup and disaster recovery

## Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure AWS credentials have required permissions
2. **Bucket Already Exists**: Script handles existing resources gracefully
3. **Lambda Timeout**: Increase timeout in Lambda configuration
4. **CORS Issues**: Verify API Gateway CORS configuration

### Rollback Procedures
If deployment fails:
1. Delete created Lambda functions
2. Remove API Gateway resources
3. Delete S3 buckets (if empty)
4. Remove DynamoDB table
5. Delete IAM roles and policies

## Cost Optimization
- Use S3 Intelligent Tiering for document storage
- Configure DynamoDB on-demand billing
- Set Lambda memory allocation based on usage
- Enable CloudWatch cost monitoring

## Security Considerations
- Enable S3 bucket encryption
- Use least privilege IAM policies
- Enable CloudTrail for audit logging
- Configure VPC endpoints for private communication

## Monitoring and Maintenance
- Set up CloudWatch alarms for errors
- Configure log retention policies
- Monitor Lambda function performance
- Regular security updates and patches