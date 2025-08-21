# Smart Expense Analyzer - API Documentation

## API Overview
The Smart Expense Analyzer provides a RESTful API for expense management operations. All endpoints use HTTPS and return JSON responses.

**Base URL**: `https://{api-id}.execute-api.{region}.amazonaws.com/prod`

## Authentication
Currently, the API uses AWS IAM for authentication. Future versions will support API keys and OAuth 2.0.

## Endpoints

### 1. Upload Expense Document

**Endpoint**: `POST /upload`

**Description**: Upload a receipt or expense document for processing.

**Request Headers**:
```
Content-Type: multipart/form-data
```

**Request Body**:
```
file: (binary) - Image or PDF file
```

**Supported File Types**:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- PDF (.pdf)
- Maximum file size: 10MB

**Response**:
```json
{
  "statusCode": 200,
  "body": {
    "message": "File uploaded successfully",
    "expense_id": "uuid-string",
    "s3_key": "uploads/filename.jpg",
    "processing_status": "queued"
  }
}
```

**Error Responses**:
```json
{
  "statusCode": 400,
  "body": {
    "error": "Invalid file type",
    "message": "Only JPEG, PNG, and PDF files are supported"
  }
}
```

**Example cURL**:
```bash
curl -X POST \
  https://api-id.execute-api.us-east-1.amazonaws.com/prod/upload \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@receipt.jpg'
```

### 2. Get Expenses

**Endpoint**: `GET /expenses`

**Description**: Retrieve expense records with optional filtering.

**Query Parameters**:
- `month` (optional): Filter by month (YYYY-MM format)
- `category` (optional): Filter by expense category
- `limit` (optional): Maximum number of records (default: 50)
- `start_key` (optional): Pagination token for next page

**Response**:
```json
{
  "statusCode": 200,
  "body": {
    "expenses": [
      {
        "expense_id": "uuid-string",
        "amount": 25.50,
        "category": "food",
        "description": "Starbucks Coffee",
        "date": "2024-01-15",
        "vendor": "Starbucks",
        "document_url": "https://s3.amazonaws.com/bucket/file.jpg",
        "processed_date": "2024-01-15T10:30:00Z",
        "confidence_score": 0.95
      }
    ],
    "total_count": 1,
    "next_page_token": "pagination-token"
  }
}
```

**Example Requests**:
```bash
# Get all expenses
curl https://api-id.execute-api.us-east-1.amazonaws.com/prod/expenses

# Get expenses for January 2024
curl "https://api-id.execute-api.us-east-1.amazonaws.com/prod/expenses?month=2024-01"

# Get food expenses
curl "https://api-id.execute-api.us-east-1.amazonaws.com/prod/expenses?category=food"
```

### 3. Get Expense by ID

**Endpoint**: `GET /expenses/{expense_id}`

**Description**: Retrieve a specific expense record by ID.

**Path Parameters**:
- `expense_id`: UUID of the expense record

**Response**:
```json
{
  "statusCode": 200,
  "body": {
    "expense_id": "uuid-string",
    "amount": 25.50,
    "category": "food",
    "description": "Starbucks Coffee",
    "date": "2024-01-15",
    "vendor": "Starbucks",
    "document_url": "https://s3.amazonaws.com/bucket/file.jpg",
    "processed_date": "2024-01-15T10:30:00Z",
    "confidence_score": 0.95,
    "raw_text": "Extracted OCR text...",
    "processing_details": {
      "textract_job_id": "job-id",
      "processing_time_ms": 1500
    }
  }
}
```

### 4. Update Expense

**Endpoint**: `PUT /expenses/{expense_id}`

**Description**: Update an existing expense record.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "amount": 30.00,
  "category": "food",
  "description": "Updated description",
  "vendor": "Updated vendor"
}
```

**Response**:
```json
{
  "statusCode": 200,
  "body": {
    "message": "Expense updated successfully",
    "expense_id": "uuid-string",
    "updated_fields": ["amount", "description"]
  }
}
```

### 5. Delete Expense

**Endpoint**: `DELETE /expenses/{expense_id}`

**Description**: Delete an expense record.

**Response**:
```json
{
  "statusCode": 200,
  "body": {
    "message": "Expense deleted successfully",
    "expense_id": "uuid-string"
  }
}
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

### Error Response Format
```json
{
  "statusCode": 400,
  "body": {
    "error": "ValidationError",
    "message": "Detailed error description",
    "request_id": "correlation-id",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Rate Limiting
- Default: 100 requests per minute per IP
- Burst: 200 requests
- Headers included in response:
  - `X-RateLimit-Limit`: Rate limit ceiling
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets

## CORS Configuration
The API supports Cross-Origin Resource Sharing (CORS) with the following configuration:
- **Allowed Origins**: `*` (configurable)
- **Allowed Methods**: `GET, POST, PUT, DELETE, OPTIONS`
- **Allowed Headers**: `Content-Type, Authorization, X-Requested-With`
- **Max Age**: 3600 seconds

## SDK and Client Libraries

### JavaScript/Node.js
```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'https://api-id.execute-api.us-east-1.amazonaws.com/prod',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Upload file
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  return response.data;
};

// Get expenses
const getExpenses = async (filters = {}) => {
  const response = await api.get('/expenses', { params: filters });
  return response.data;
};
```

### Python
```python
import requests

class ExpenseAnalyzerAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        
    def upload_file(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/upload", files=files)
            return response.json()
    
    def get_expenses(self, **filters):
        response = requests.get(f"{self.base_url}/expenses", params=filters)
        return response.json()

# Usage
api = ExpenseAnalyzerAPI('https://api-id.execute-api.us-east-1.amazonaws.com/prod')
result = api.upload_file('receipt.jpg')
expenses = api.get_expenses(month='2024-01')
```

## Postman Collection
A Postman collection is available for testing the API endpoints:

```json
{
  "info": {
    "name": "Smart Expense Analyzer API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Upload Document",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": []
            }
          ]
        },
        "url": {
          "raw": "{{baseUrl}}/upload",
          "host": ["{{baseUrl}}"],
          "path": ["upload"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://api-id.execute-api.us-east-1.amazonaws.com/prod"
    }
  ]
}
```

## Testing and Validation

### Unit Tests
```python
import unittest
from unittest.mock import patch, MagicMock

class TestExpenseAPI(unittest.TestCase):
    def test_upload_valid_file(self):
        # Test file upload with valid image
        pass
    
    def test_get_expenses_with_filters(self):
        # Test expense retrieval with filters
        pass
    
    def test_invalid_file_type(self):
        # Test error handling for invalid file types
        pass
```

### Integration Tests
```bash
# Test file upload
curl -X POST -F "file=@test_receipt.jpg" \
  https://api-id.execute-api.us-east-1.amazonaws.com/prod/upload

# Test expense retrieval
curl https://api-id.execute-api.us-east-1.amazonaws.com/prod/expenses
```