# Smart Expense Analyzer - AWS Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AWS CLOUD ENVIRONMENT                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────┐ │
│  │   USERS/WEB     │    │   PRESENTATION   │    │        SECURITY             │ │
│  │                 │    │      LAYER       │    │                             │ │
│  │ • Web Browser   │◄──►│ • S3 Static Web  │    │ • IAM Roles & Policies      │ │
│  │ • Mobile App    │    │ • CloudFront CDN │    │ • VPC (Optional)            │ │
│  │ • API Clients   │    │ • Route 53 DNS   │    │ • Security Groups           │ │
│  └─────────────────┘    └──────────────────┘    └─────────────────────────────┘ │
│           │                       │                           │                 │
│           │                       │                           │                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           API GATEWAY LAYER                                 │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐ │ │
│  │  │  API Gateway    │    │   CORS Config   │    │    Rate Limiting        │ │ │
│  │  │                 │    │                 │    │                         │ │ │
│  │  │ • REST API      │    │ • Cross-Origin  │    │ • Throttling            │ │ │
│  │  │ • Authentication│    │ • Headers       │    │ • Usage Plans           │ │ │
│  │  │ • Request/Resp  │    │ • Methods       │    │ • API Keys              │ │ │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│           │                       │                           │                 │
│           │                       │                           │                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         COMPUTE LAYER (SERVERLESS)                          │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐ │ │
│  │  │ Lambda Function │    │ Lambda Function │    │   Lambda Function       │ │ │
│  │  │                 │    │                 │    │                         │ │ │
│  │  │ process_document│    │  get_expenses   │    │    upload_api           │ │ │
│  │  │                 │    │                 │    │                         │ │ │
│  │  │ • OCR Processing│    │ • Data Retrieval│    │ • File Upload Handler   │ │ │
│  │  │ • Text Extract  │    │ • JSON Response │    │ • Validation            │ │ │
│  │  │ • Categorization│    │ • CORS Headers  │    │ • S3 Integration        │ │ │
│  │  │ • Data Validation│   │ • Error Handling│    │ • Error Handling        │ │ │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│           │                       │                           │                 │
│           │                       │                           │                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           STORAGE LAYER                                     │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐ │ │
│  │  │   Amazon S3     │    │   DynamoDB      │    │    CloudWatch Logs      │ │ │
│  │  │                 │    │                 │    │                         │ │ │
│  │  │ • Document Store│    │ • Expense Data  │    │ • Application Logs      │ │ │
│  │  │ • Static Website│    │ • NoSQL Database│    │ • Error Tracking        │ │ │
│  │  │ • Versioning    │    │ • Auto Scaling  │    │ • Performance Metrics   │ │ │
│  │  │ • Lifecycle     │    │ • Point-in-Time │    │ • Monitoring            │ │ │
│  │  │ • Encryption    │    │   Recovery      │    │                         │ │ │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│           │                       │                           │                 │
│           │                       │                           │                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         AI/ML SERVICES LAYER                               │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐ │ │
│  │  │  AWS Textract   │    │  Amazon Rekogn. │    │    Future ML Services   │ │ │
│  │  │                 │    │   (Optional)    │    │                         │ │ │
│  │  │ • OCR Processing│    │ • Image Analysis│    │ • Amazon Comprehend     │ │ │
│  │  │ • Text Detection│    │ • Object Detect │    │ • Custom ML Models      │ │ │
│  │  │ • Document AI   │    │ • Text in Images│    │ • SageMaker Integration │ │ │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    USER     │    │   UPLOAD    │    │  PROCESSING │    │   STORAGE   │
│             │    │             │    │             │    │             │
│ 1. Upload   │───►│ 2. S3 Event │───►│ 3. Lambda   │───►│ 4. DynamoDB │
│    Receipt  │    │    Trigger  │    │   Process   │    │   Storage   │
│             │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                                      │                   │
       │                                      │                   │
       │            ┌─────────────┐          │                   │
       │            │  TEXTRACT   │          │                   │
       │            │             │          │                   │
       └────────────┤ 5. OCR Text │◄─────────┘                   │
                    │  Extraction │                              │
                    │             │                              │
                    └─────────────┘                              │
                                                                 │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│  DASHBOARD  │    │   RETRIEVE  │    │    QUERY    │           │
│             │    │             │    │             │           │
│ 8. Display  │◄───│ 7. Generate │◄───│ 6. Fetch    │◄──────────┘
│   Results   │    │    HTML     │    │    Data     │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## AWS Best Practices Implementation

### 1. Security Best Practices
```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  IAM POLICIES   │    │   ENCRYPTION    │                │
│  │                 │    │                 │                │
│  │ • Least Privilege│   │ • S3 Encryption │                │
│  │ • Role-based    │    │ • DDB Encryption│                │
│  │ • Resource ARNs │    │ • TLS in Transit│                │
│  │ • Condition Keys│    │ • KMS Keys      │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  MONITORING     │    │   COMPLIANCE    │                │
│  │                 │    │                 │                │
│  │ • CloudTrail    │    │ • Data Privacy  │                │
│  │ • CloudWatch    │    │ • GDPR Ready    │                │
│  │ • AWS Config    │    │ • Audit Logs    │                │
│  │ • GuardDuty     │    │ • Retention     │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### 2. Reliability & Availability
```
┌─────────────────────────────────────────────────────────────┐
│                 RELIABILITY PATTERNS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  MULTI-AZ       │    │   ERROR HANDLING│                │
│  │                 │    │                 │                │
│  │ • DynamoDB      │    │ • Retry Logic   │                │
│  │   Global Tables │    │ • Circuit Break │                │
│  │ • S3 Cross-Reg  │    │ • Graceful Fail │                │
│  │ • Lambda Multi  │    │ • Dead Letter Q │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   BACKUP &      │    │   MONITORING    │                │
│  │   RECOVERY      │    │                 │                │
│  │                 │    │ • Health Checks │                │
│  │ • Point-in-Time │    │ • Alarms        │                │
│  │ • Versioning    │    │ • Dashboards    │                │
│  │ • Snapshots     │    │ • Notifications │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### 3. Performance Optimization
```
┌─────────────────────────────────────────────────────────────┐
│               PERFORMANCE OPTIMIZATION                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │    CACHING      │    │   SCALING       │                │
│  │                 │    │                 │                │
│  │ • CloudFront    │    │ • Auto Scaling  │                │
│  │ • API Gateway   │    │ • Lambda Concur │                │
│  │ • DynamoDB DAX  │    │ • DDB On-Demand │                │
│  │ • Browser Cache│    │ • Elastic Scale │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  OPTIMIZATION   │    │   COST CONTROL  │                │
│  │                 │    │                 │                │
│  │ • Memory Tuning │    │ • Reserved Cap  │                │
│  │ • Timeout Config│    │ • Lifecycle Pol │                │
│  │ • Batch Process │    │ • Usage Monitor │                │
│  │ • Async Pattern │    │ • Cost Alerts   │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Lambda Functions Configuration
```yaml
process_document:
  runtime: python3.9
  memory: 512MB
  timeout: 300s
  environment:
    - DYNAMODB_TABLE: ExpenseRecords
    - S3_BUCKET: expense-documents
  
get_expenses:
  runtime: python3.9
  memory: 256MB
  timeout: 30s
  environment:
    - DYNAMODB_TABLE: ExpenseRecords

upload_api:
  runtime: python3.9
  memory: 256MB
  timeout: 60s
  environment:
    - S3_BUCKET: expense-documents
```

### DynamoDB Table Design
```yaml
ExpenseRecords:
  partition_key: expense_id (String)
  sort_key: processed_at (String)
  attributes:
    - amount (Number)
    - category (String)
    - description (String)
    - date (String)
    - s3_key (String)
    - raw_text (String)
  
  global_secondary_indexes:
    - GSI1:
        partition_key: category
        sort_key: date
    - GSI2:
        partition_key: date
        sort_key: amount
```

### S3 Bucket Configuration
```yaml
expense-documents:
  versioning: enabled
  encryption: AES256
  lifecycle_policy:
    - transition_to_ia: 30_days
    - transition_to_glacier: 90_days
    - expire: 2555_days
  
expense-frontend:
  static_website: enabled
  public_read: true
  cloudfront_distribution: enabled
```

This architecture follows AWS Well-Architected Framework principles:
- **Security**: IAM roles, encryption, monitoring
- **Reliability**: Multi-AZ, error handling, backups
- **Performance**: Caching, auto-scaling, optimization
- **Cost Optimization**: Serverless, lifecycle policies
- **Operational Excellence**: Monitoring, logging, automation