# Smart Expense Analyzer - Developer Guide

## Development Environment Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 14+ (for frontend development)
- AWS CLI configured
- Git for version control
- Code editor (VS Code recommended)

### Local Development Setup

1. **Clone Repository**
```bash
git clone <repository-url>
cd smart-expense-analyzer
```

2. **Python Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. **Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your AWS credentials and settings
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

4. **Local Testing Setup**
```bash
# Install development dependencies
pip install pytest pytest-cov moto boto3-stubs

# Run tests
pytest tests/ -v --cov=backend/
```

## Project Structure

```
smart-expense-analyzer/
├── backend/                    # Lambda function code
│   ├── process_document.py    # OCR processing logic
│   ├── get_expenses.py        # Data retrieval API
│   ├── upload_api.py          # File upload handler
│   └── utils/                 # Shared utilities
│       ├── __init__.py
│       ├── validation.py      # Data validation
│       ├── categorization.py  # Expense categorization
│       └── aws_helpers.py     # AWS service helpers
├── frontend/                  # Static web assets
│   ├── index.html            # Main dashboard
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   └── assets/               # Images and icons
├── tests/                    # Test files
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── fixtures/             # Test data
├── docs/                     # Documentation
├── scripts/                  # Deployment scripts
│   ├── deploy-infrastructure.py
│   ├── deploy-lambdas.py
│   └── generate_static_html.py
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
└── README.md               # Project overview
```

## Code Organization

### Backend Architecture

**Lambda Functions**:
- Each function has a single responsibility
- Shared code in `utils/` module
- Environment-specific configuration
- Comprehensive error handling

**Code Style**:
- Follow PEP 8 Python style guide
- Use type hints for function parameters
- Docstrings for all public functions
- Maximum line length: 88 characters

**Example Function Structure**:
```python
import json
import logging
from typing import Dict, Any
from utils.validation import validate_expense_data
from utils.aws_helpers import get_dynamodb_table

logger = logging.getLogger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process expense document upload.
    
    Args:
        event: Lambda event data
        context: Lambda context object
        
    Returns:
        API Gateway response format
    """
    try:
        # Function implementation
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Success'})
        }
    except Exception as e:
        logger.error(f"Function error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
```

### Frontend Architecture

**Technology Stack**:
- Vanilla JavaScript (ES6+)
- CSS3 with Flexbox/Grid
- Responsive design principles
- Progressive Web App features

**File Organization**:
```
frontend/
├── index.html              # Main page
├── css/
│   ├── main.css           # Main styles
│   ├── components.css     # Component styles
│   └── responsive.css     # Mobile styles
├── js/
│   ├── app.js            # Main application logic
│   ├── api.js            # API communication
│   ├── components.js     # UI components
│   └── utils.js          # Utility functions
└── assets/
    ├── icons/            # SVG icons
    └── images/           # Images and logos
```

## Development Workflow

### Git Workflow
We use GitFlow branching strategy:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches
- `hotfix/*`: Critical bug fixes
- `release/*`: Release preparation

### Branch Naming Convention
```
feature/expense-categorization
bugfix/upload-validation-error
hotfix/security-vulnerability
release/v1.2.0
```

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(backend): add expense categorization logic
fix(frontend): resolve upload button styling issue
docs(api): update endpoint documentation
```

### Pull Request Process

1. **Create Feature Branch**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/new-feature
```

2. **Development and Testing**
```bash
# Make changes
git add .
git commit -m "feat(scope): description"

# Run tests
pytest tests/ -v
npm test  # if frontend changes
```

3. **Push and Create PR**
```bash
git push origin feature/new-feature
# Create pull request via GitHub/GitLab
```

4. **Code Review Checklist**
- [ ] Code follows style guidelines
- [ ] Tests pass and coverage maintained
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered

## Testing Strategy

### Unit Testing

**Backend Tests**:
```python
# tests/unit/test_process_document.py
import pytest
from moto import mock_textract, mock_dynamodb
from backend.process_document import extract_expense_info

@mock_textract
@mock_dynamodb
def test_extract_expense_info():
    # Test OCR text extraction
    sample_text = "Starbucks Coffee\nTotal: $4.85\nDate: 01/15/2024"
    result = extract_expense_info(sample_text, "receipt.jpg")
    
    assert result['amount'] == 4.85
    assert result['category'] == 'food'
    assert result['vendor'] == 'Starbucks'
```

**Frontend Tests**:
```javascript
// tests/frontend/test_api.js
describe('API Client', () => {
  test('should upload file successfully', async () => {
    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const result = await uploadFile(mockFile);
    
    expect(result.statusCode).toBe(200);
    expect(result.body.message).toBe('File uploaded successfully');
  });
});
```

### Integration Testing

**API Integration Tests**:
```python
# tests/integration/test_api_endpoints.py
import requests
import pytest

class TestAPIEndpoints:
    def setup_class(self):
        self.base_url = "https://api-id.execute-api.us-east-1.amazonaws.com/prod"
    
    def test_upload_endpoint(self):
        with open('tests/fixtures/sample_receipt.jpg', 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/upload", files=files)
        
        assert response.status_code == 200
        assert 'expense_id' in response.json()['body']
```

### End-to-End Testing

**Selenium Tests**:
```python
# tests/e2e/test_user_workflow.py
from selenium import webdriver
from selenium.webdriver.common.by import By

class TestUserWorkflow:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://expense-analyzer-frontend.s3-website-us-east-1.amazonaws.com")
    
    def test_upload_and_view_expense(self):
        # Test complete user workflow
        upload_button = self.driver.find_element(By.ID, "upload-button")
        upload_button.click()
        
        # Upload file and verify processing
        # ... test implementation
```

## Debugging and Troubleshooting

### Local Development Debugging

**Lambda Function Testing**:
```python
# local_test.py
import json
from backend.process_document import lambda_handler

# Mock event data
event = {
    'Records': [{
        's3': {
            'bucket': {'name': 'test-bucket'},
            'object': {'key': 'test-file.jpg'}
        }
    }]
}

# Test locally
result = lambda_handler(event, None)
print(json.dumps(result, indent=2))
```

**AWS Local Testing with SAM**:
```bash
# Install SAM CLI
pip install aws-sam-cli

# Create SAM template
sam init

# Test locally
sam local start-api
sam local invoke ProcessDocumentFunction --event events/s3-event.json
```

### Production Debugging

**CloudWatch Logs**:
```python
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Processing event: {json.dumps(event)}")
    
    try:
        # Function logic
        result = process_document(event)
        logger.info(f"Processing successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        raise
```

**X-Ray Tracing**:
```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch AWS services
patch_all()

@xray_recorder.capture('process_document')
def lambda_handler(event, context):
    # Function implementation with tracing
    pass
```

## Performance Optimization

### Lambda Optimization

**Cold Start Reduction**:
```python
# Global variables for connection reuse
import boto3

# Initialize outside handler
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ExpenseRecords')

def lambda_handler(event, context):
    # Use pre-initialized resources
    pass
```

**Memory and Timeout Tuning**:
- Monitor CloudWatch metrics
- Adjust memory allocation based on usage
- Set appropriate timeout values
- Use provisioned concurrency for critical functions

### Frontend Optimization

**Performance Best Practices**:
- Minimize HTTP requests
- Compress images and assets
- Use CDN for static content
- Implement lazy loading
- Cache API responses

**Code Splitting**:
```javascript
// Dynamic imports for code splitting
const loadDashboard = async () => {
  const { Dashboard } = await import('./components/Dashboard.js');
  return Dashboard;
};
```

## Security Best Practices

### Code Security

**Input Validation**:
```python
def validate_file_upload(file_data):
    # File type validation
    allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
    if file_data['content_type'] not in allowed_types:
        raise ValueError("Invalid file type")
    
    # File size validation
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_data['content']) > max_size:
        raise ValueError("File too large")
    
    return True
```

**SQL Injection Prevention**:
```python
# Use parameterized queries
def get_expenses_by_category(category):
    # DynamoDB automatically handles injection prevention
    response = table.query(
        IndexName='CategoryIndex',
        KeyConditionExpression=Key('category').eq(category)
    )
    return response['Items']
```

**Secrets Management**:
```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# Use in code
api_key = get_secret('third-party-api-key')
```

### Infrastructure Security

**IAM Policies**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
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
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/ExpenseRecords"
    }
  ]
}
```

## Deployment and Release

### Continuous Integration

**GitHub Actions Workflow**:
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest tests/ -v --cov=backend/
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Release Process

1. **Version Bumping**
```bash
# Update version in setup.py or __version__.py
git add .
git commit -m "chore: bump version to 1.2.0"
git tag v1.2.0
git push origin main --tags
```

2. **Deployment**
```bash
# Deploy to staging
python scripts/deploy-infrastructure.py --env staging
python scripts/deploy-lambdas.py --env staging

# Run tests
python test_deployment.py --env staging

# Deploy to production
python scripts/deploy-infrastructure.py --env production
python scripts/deploy-lambdas.py --env production
```

3. **Rollback Procedure**
```bash
# Rollback Lambda functions
aws lambda update-function-code \
  --function-name process_document \
  --s3-bucket deployment-bucket \
  --s3-key previous-version.zip

# Rollback infrastructure if needed
terraform apply -var-file="previous-version.tfvars"
```

## Contributing Guidelines

### Code Review Standards
- All code must be reviewed by at least one other developer
- Automated tests must pass
- Code coverage should not decrease
- Documentation must be updated for new features

### Issue Reporting
- Use GitHub Issues for bug reports and feature requests
- Include reproduction steps for bugs
- Provide clear acceptance criteria for features

### Community Guidelines
- Be respectful and inclusive
- Follow the code of conduct
- Help others learn and grow
- Share knowledge through documentation and examples