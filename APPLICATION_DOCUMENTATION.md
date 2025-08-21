# Smart Expense Analyzer - Application Documentation

## Application Overview
The Smart Expense Analyzer is a serverless AWS application that automatically processes expense receipts using OCR technology and provides a web-based dashboard for expense management.

## Architecture Components

### Frontend Layer
- **Technology**: Static HTML/CSS/JavaScript
- **Hosting**: Amazon S3 with static website hosting
- **Features**: 
  - File upload interface
  - Expense dashboard with filtering
  - Responsive design for mobile/desktop

### API Layer
- **Technology**: Amazon API Gateway (REST API)
- **Endpoints**:
  - `POST /upload` - File upload endpoint
  - `GET /expenses` - Retrieve expense data
- **Features**: CORS enabled, rate limiting, error handling

### Compute Layer
- **Technology**: AWS Lambda (Python 3.8)
- **Functions**:
  - `process_document` - OCR processing and data extraction
  - `get_expenses` - Data retrieval from DynamoDB
  - `upload_api` - File upload handling

### Storage Layer
- **Document Storage**: Amazon S3
  - Bucket: `expense-analyzer-documents`
  - Lifecycle policies for cost optimization
- **Data Storage**: Amazon DynamoDB
  - Table: `ExpenseRecords`
  - On-demand billing mode

### AI/ML Services
- **OCR Processing**: Amazon Textract
- **Text Analysis**: Custom categorization logic
- **Data Extraction**: Pattern matching for amounts, dates, vendors

## Data Models

### Expense Record Schema
```json
{
  "expense_id": "string (UUID)",
  "amount": "decimal",
  "category": "string",
  "description": "string", 
  "date": "string (YYYY-MM-DD)",
  "vendor": "string",
  "document_url": "string",
  "processed_date": "string (ISO timestamp)",
  "confidence_score": "decimal"
}
```

### Supported Categories
- Food & Dining
- Transportation
- Office Supplies
- Healthcare
- Entertainment
- Utilities
- Other

## Business Logic

### Document Processing Workflow
1. User uploads receipt image/PDF
2. File stored in S3 triggers Lambda function
3. Textract extracts text from document
4. Custom logic categorizes and extracts key data
5. Validated data stored in DynamoDB
6. Dashboard updated with new expense

### Data Validation Rules
- Amount must be positive decimal
- Date must be valid format (YYYY-MM-DD)
- Category must be from predefined list
- Description cannot be empty
- Vendor name extracted from document text

### Error Handling
- Invalid file formats rejected
- OCR failures logged and user notified
- Database errors handled gracefully
- Retry logic for transient failures

## Integration Points

### External Dependencies
- AWS Textract API for OCR processing
- S3 for file storage and static hosting
- DynamoDB for data persistence
- API Gateway for HTTP endpoints

### Internal Dependencies
- Lambda functions communicate via S3 events
- Shared utility functions for data validation
- Common error handling patterns

## Performance Characteristics

### Response Times
- File upload: < 2 seconds
- OCR processing: 5-15 seconds (async)
- Dashboard load: < 1 second
- Expense retrieval: < 500ms

### Scalability
- Lambda auto-scales to handle concurrent requests
- DynamoDB scales based on demand
- S3 provides unlimited storage capacity
- API Gateway handles high request volumes

### Throughput Limits
- Lambda: 1000 concurrent executions (default)
- API Gateway: 10,000 requests/second
- DynamoDB: 40,000 read/write units on-demand
- Textract: 600 pages/minute

## Monitoring and Logging

### CloudWatch Metrics
- Lambda function duration and errors
- API Gateway request count and latency
- DynamoDB read/write capacity utilization
- S3 storage usage and requests

### Log Aggregation
- Lambda function logs in CloudWatch Logs
- API Gateway access logs
- Application-level error logging
- Structured logging with correlation IDs

### Alerting
- Lambda function errors > threshold
- API Gateway 5xx errors
- DynamoDB throttling events
- High cost usage alerts

## Backup and Disaster Recovery

### Data Backup
- DynamoDB point-in-time recovery enabled
- S3 versioning for document storage
- Cross-region replication for critical data
- Automated backup schedules

### Recovery Procedures
- Database restore from point-in-time
- Lambda function redeployment
- S3 bucket restoration
- Infrastructure as Code for quick rebuild

## Security Implementation

### Authentication & Authorization
- IAM roles with least privilege access
- API Gateway resource-based policies
- S3 bucket policies for secure access
- Lambda execution role permissions

### Data Protection
- S3 server-side encryption (SSE-S3)
- DynamoDB encryption at rest
- TLS 1.2 for data in transit
- Secure API endpoints (HTTPS only)

### Compliance
- GDPR-ready data handling
- Data retention policies
- Audit trail via CloudTrail
- Regular security assessments