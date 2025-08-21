# Amazon Q User Prompt - Smart Expense Analyzer Application

## Complete User Prompt for Amazon Q

```
create a comprehensive serverless Smart Expense Analyzer application from scratch on AWS that automatically processes receipt images and documents to extract expense information with robust error handling and production-ready features.

CORE REQUIREMENTS:
- Upload receipt images (JPG, PNG, PDF) and plain text files through web interface
- Automatically extract expense details using AWS Textract OCR for images/PDFs
- Direct text processing for .txt files without OCR overhead
- Intelligent expense categorization based on keyword analysis (food, transport, office, healthcare, travel, other)
- Store expense records in DynamoDB with comprehensive metadata and validation
- Generate interactive visual dashboard with month-wise filtering capabilities
- Real-time processing with comprehensive error handling and fallback mechanisms

TECHNICAL ARCHITECTURE:
- AWS Lambda functions for serverless document processing with proper memory/timeout configuration
- AWS Textract for optical character recognition on images and PDFs
- DynamoDB for persistent expense data storage with Decimal precision for amounts
- S3 bucket integration for document storage with lifecycle policies
- Static HTML generation from DynamoDB data for offline dashboard viewing
- JavaScript-based interactivity for month filtering and dynamic category display
- CORS-enabled API endpoints for cross-origin requests

CRITICAL ERROR HANDLING & VALIDATION:
- Comprehensive input validation for all extracted fields before database insertion
- Amount validation ensuring positive Decimal values only with proper regex patterns
- Enhanced date parsing supporting multiple formats (MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD) with two-digit year handling
- Required field checking with detailed error logging for debugging
- Graceful handling of AWS credential expiration with informative error messages
- Fallback sample data for development/testing when AWS services unavailable
- Continue processing on individual document failures without stopping batch
- File type validation to prevent unsupported format processing
- S3 upload failure recovery with local file retention
- Textract service limit handling with graceful degradation

ADVANCED PROCESSING FEATURES:
- Multi-pattern amount extraction with validation (Total, Amount, currency symbols, standalone amounts)
- Business name and description extraction from receipt text with filename fallback
- Batch processing support for multiple documents with processing count tracking
- Processing status tracking and detailed error reporting with specific failure reasons
- Memory-efficient handling of large documents with text truncation (500 chars)
- Optimized text processing with early pattern matching for performance

ENHANCED USER EXPERIENCE:
- Month-wise expense filtering with dynamic dropdown population from actual data
- Category-based expense breakdown with sorting by amount (highest first)
- Responsive design with gradient styling and hover effects for modern UI
- Real-time processing feedback and status updates with success/error messages
- Processing count tracking and summary statistics display
- Mobile-friendly interface with touch-optimized controls
- Auto-generated month options based on actual expense data in database

ROBUST DATA STRUCTURE:
Each expense record must include:
- Unique UUID identifier for tracking
- Decimal-precision amount with validation (no negative values)
- Intelligent category classification with keyword matching
- Extracted description (business name extraction or filename fallback)
- Parsed date with multiple format support and current date fallback
- ISO timestamp for processing time tracking
- S3 key reference for source document traceability
- Raw extracted text (truncated to 500 characters for storage efficiency)
- Validation status and error flags for debugging

INFRASTRUCTURE RESILIENCE:
- AWS credential expiration handling with try-catch blocks and informative messages
- DynamoDB connection error handling with retry logic
- Network timeout handling for large file processing
- Resource cleanup on processing failures to prevent memory leaks
- Environment-specific configuration support for dev/staging/prod
- Proper IAM roles with least privilege access principles

SECURITY & PERFORMANCE:
- Input sanitization for all user-provided data to prevent injection attacks
- Efficient database queries with proper indexing strategies
- Serverless architecture for automatic scaling and cost optimization
- File type validation to prevent malicious uploads
- Proper error message sanitization to prevent information leakage
- Memory usage optimization for Lambda functions

DEPLOYMENT & MAINTENANCE:
- Automated HTML generation with embedded data from DynamoDB
- Static file deployment to S3 with proper content types and caching headers
- Local development support with sample data fallbacks for testing
- Comprehensive logging for debugging and monitoring with CloudWatch integration
- Modular code structure for easy maintenance and updates
- Environment variable configuration for different deployment stages

SPECIFIC IMPLEMENTATION DETAILS:
- Use Python 3.9+ for Lambda functions with boto3 for AWS service integration
- Implement proper exception handling with specific error types (ValueError, ArithmeticError)
- Use regex patterns for amount extraction: r'Total[:\s]*\$?([0-9]+(?:\.[0-9]{2})?)'
- Date parsing with multiple format attempts and century correction for 2-digit years
- DynamoDB table design with partition key (expense_id) and sort key (processed_at)
- S3 event triggers for automatic document processing on upload
- CORS configuration for API Gateway with proper headers
- Lambda memory configuration: 512MB for processing, 256MB for API functions
- Timeout settings: 300s for processing, 30s for API calls

TESTING & QUALITY ASSURANCE:
- Include comprehensive test cases for all extraction patterns
- Sample receipt images for different categories and formats
- Error simulation tests for AWS service failures
- Validation tests for edge cases (zero amounts, invalid dates, empty text)
- Performance testing for large document processing
- Integration testing for complete workflow from upload to dashboard

COST OPTIMIZATION:
- Implement S3 lifecycle policies for document archival
- Use DynamoDB on-demand pricing for variable workloads
- Optimize Lambda memory allocation based on actual usage
- Implement CloudWatch monitoring for cost tracking
- Use efficient data structures to minimize storage costs

MONITORING & OBSERVABILITY:
- CloudWatch logs integration for all Lambda functions
- Error tracking with detailed stack traces
- Performance metrics monitoring (processing time, success rates)
- Cost monitoring with billing alerts
- Health check endpoints for system status

Create a complete, production-ready application that handles all these requirements with proper error handling, validation, and user experience. Include all necessary files: Lambda functions, HTML frontend, deployment scripts, documentation, and configuration files. Ensure the application is resilient to common AWS service issues and provides meaningful error messages to users.
```

## Additional Instructions for Amazon Q

When using this prompt with Amazon Q, also specify:

1. **File Structure**: Request specific file organization with backend/, frontend/, tests/, docs/ folders
2. **Documentation**: Ask for README.md, deployment guides, and API documentation
3. **Configuration**: Request environment variables, IAM policies, and AWS resource configurations
4. **Testing**: Ask for unit tests, integration tests, and sample data
5. **Deployment**: Request infrastructure as code (CloudFormation/Terraform) and deployment scripts

## Usage Tips

- Use this prompt in Amazon Q's agentic coding mode for full file creation capabilities
- Break into smaller chunks if the response is too large
- Ask for specific components if you need to focus on particular areas
- Request code reviews and optimizations after initial generation