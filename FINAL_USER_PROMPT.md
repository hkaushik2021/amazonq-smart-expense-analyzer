# Smart Expense Analyzer - AWS Serverless Application

Create a complete serverless expense tracking application using AWS services with automatic document processing and web dashboard.

## Core Requirements

**Application Features:**
- Upload receipts/documents (JPG, PNG, PDF, TXT)
- Automatic text extraction using AWS Textract
- Expense categorization and amount detection
- Web dashboard showing expense summaries by category and month
- Integrated upload page with drag-and-drop functionality

**AWS Architecture:**
- S3 buckets for document storage and website hosting
- DynamoDB table for expense records
- Lambda functions for processing and API endpoints
- API Gateway for REST endpoints
- Textract for document text extraction

## Key Issues to Handle

**API Permission Fixing:**
- Add `--fix-permissions` flag to deploy-infrastructure.py
- Fix "Forbidden" errors by removing old Lambda permissions and adding correct ones
- Automatically redeploy API Gateway after fixing permissions
- NO separate fix files - integrate permission fixing into main infrastructure script
- Usage: `python deploy-infrastructure.py --fix-permissions`

**CORS Configuration:**
- Configure OPTIONS methods for all API Gateway endpoints
- Add proper CORS headers in Lambda responses
- Handle preflight requests correctly

**Frontend Integration:**
- Create upload-receipt.html page with drag-and-drop file upload functionality
- Integrate upload page into main dashboard with navigation buttons
- Add "Upload Receipt" button on main dashboard linking to upload page
- Add "Home" button on upload page linking back to main dashboard ("/")
- Include proper CORS configuration for API Gateway with OPTIONS methods
- Deploy both pages to S3 website hosting automatically

**Error Handling:**
- Resource existence checks to prevent creation conflicts
- Proper error messages and fallback mechanisms
- Handle credential and service failures gracefully
- Dashboard must handle API response format variations gracefully
- Include comprehensive error logging for API call debugging

## Deployment Requirements

**Infrastructure Setup:**
- Create S3 buckets with proper permissions and website hosting
- Create DynamoDB table with pay-per-request billing
- Create IAM roles with minimal required permissions
- Create API Gateway with CORS support

**Lambda Functions:**
1. `process_document` - Triggered by S3 uploads, uses Textract to extract text and categorize expenses
2. `get_expenses` - API endpoint to retrieve expense data from DynamoDB
3. `upload_api` - API endpoint to handle file uploads to S3

**Frontend:**
- Dynamic HTML dashboard showing expense summaries
- Dashboard must call API endpoints dynamically to get real-time data instead of using static data
- Handle different API response formats including arrays, wrapped objects, and DynamoDB Items format
- Include auto-refresh functionality and manual refresh button
- Upload page with drag-and-drop file upload
- Navigation between dashboard and upload page
- Responsive design for mobile and desktop
- Set cache-busting headers to prevent browser caching of old data

## Testing Requirements

**Consolidated Testing Approach:**
- Create SINGLE comprehensive test_deployment.py that verifies all AWS resources
- Test S3 bucket accessibility and website hosting
- Verify DynamoDB table creation and data access
- Check Lambda function deployment and configuration
- Validate API Gateway endpoints (GET /expenses and POST /upload) with proper JSON format
- Test frontend website accessibility and content
- Verify data processing functions work correctly
- Include API debugging and permission fixing capabilities
- Provide comprehensive pass/fail summary with URLs
- NO separate test files - everything consolidated in test_deployment.py

**Mandatory Verification:**
- **CRITICAL: Run python test_deployment.py after every deployment to verify everything works**
- **NO deployment is considered successful until all tests pass**
- Include automated rollback suggestions if tests fail

## Documentation Requirements

Create comprehensive documentation covering:

1. **README.md** - Project overview, quick start, installation
2. **DEPLOYMENT_GUIDE.md** - Step-by-step AWS setup and deployment
3. **API_DOCUMENTATION.md** - Complete API reference with examples
4. **USER_MANUAL.md** - End-user guide with screenshots
5. **DEVELOPER_GUIDE.md** - Development setup and workflow
6. **SECURITY_GUIDE.md** - Security architecture and compliance
7. **TROUBLESHOOTING.md** - Common issues and solutions
8. **ARCHITECTURE_DOCUMENTATION.md** - Technical architecture details
9. **architecture_diagrams.html** - Interactive architecture diagrams with Mermaid.js

**Architecture Diagrams Requirements:**
- System Architecture Overview with AWS service icons
- Sequence Diagram showing receipt processing flow
- AWS Services Architecture with service layers
- Cost Breakdown with pie chart and detailed table
- Technology Stack with 8 technology categories
- Scalability & Performance with growth path visualization
- Use Mermaid.js for professional diagram rendering
- Include interactive elements and responsive design
- Professional styling with gradient background and clean layout

## Deployment Scripts

**Required Scripts:**
- `deploy-infrastructure.py` - Deploy AWS infrastructure with permission fixing
- `deploy-lambdas.py` - Deploy Lambda functions with API Gateway configuration
- `generate_static_html.py` - Generate and deploy frontend files
- `test_deployment.py` - Comprehensive deployment verification
- `architecture_diagrams.html` - Interactive architecture visualization

**Key Features:**
- Handle existing resources gracefully
- Provide clear success/failure feedback
- Include rollback capabilities
- Support different AWS regions
- Handle Windows/Unix path differences

## Success Criteria

The application should:
- Deploy without manual intervention
- Handle common AWS permission issues automatically
- Provide working upload and dashboard functionality
- Pass all deployment verification tests
- Include comprehensive documentation
- Support end-to-end expense tracking workflow

This prompt ensures creation of a production-ready serverless expense analyzer that handles real-world deployment challenges and provides a smooth user experience.