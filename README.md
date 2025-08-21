# Smart Expense Analyzer

A comprehensive serverless expense tracking application that automatically processes receipt images and documents to extract expense information and categorize spending.

## Features

- 📄 **Document Processing**: Upload JPG, PNG, PDF, or TXT files
- 🤖 **AI-Powered OCR**: Automatic text extraction using AWS Textract
- 🏷️ **Smart Categorization**: Intelligent expense categorization (food, transport, office, healthcare, travel, other)
- 📊 **Interactive Dashboard**: Visual expense summaries with month-wise filtering
- 💾 **Secure Storage**: All data stored in AWS DynamoDB with S3 document backup
- 🌐 **Serverless Architecture**: Scalable and cost-effective AWS Lambda functions

## Architecture

```
User Upload → S3 → Lambda (Textract) → DynamoDB → Dashboard
```

### AWS Services Used
- **AWS Lambda**: Serverless document processing
- **AWS Textract**: OCR text extraction
- **Amazon DynamoDB**: Expense data storage
- **Amazon S3**: Document and website hosting
- **API Gateway**: REST API endpoints

## Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Python 3.9+
- boto3 library

### 1. Deploy Infrastructure
```bash
python deploy-infrastructure.py
```

### 2. Deploy Lambda Functions
```bash
python deploy-lambdas.py
```

### 3. Generate Static Dashboard
```bash
python generate_static_html.py
```

### 4. Access the Application
Once deployed, access your application at:
- **Dashboard**: `http://expense-analyzer-frontend.s3-website-{region}.amazonaws.com/`
- **Upload Page**: `http://expense-analyzer-frontend.s3-website-{region}.amazonaws.com/upload-receipt.html`

## Project Structure

```
smart-expense-analyzer/
├── backend/
│   ├── process_document.py    # Main document processing
│   ├── get_expenses.py        # Expense retrieval API
│   └── upload_api.py          # File upload handler
├── frontend/
│   ├── index.html             # Dashboard interface
│   └── upload-receipt.html    # File upload page
├── tests/
│   └── test_process_document.py # Unit tests
├── deploy-infrastructure.py   # AWS resource setup
├── deploy-lambdas.py         # Lambda deployment
├── generate_static_html.py   # Static site generator
└── requirements.txt          # Python dependencies
```

## Usage

### Upload Receipts
1. Open the dashboard in your browser
2. Click the upload area or drag and drop files
3. Supported formats: JPG, PNG, PDF, TXT
4. Files are automatically processed and categorized

### View Expenses
- **All Time**: View total expenses across all categories
- **Monthly View**: Filter expenses by specific months
- **Category Breakdown**: See spending by category with item counts

### API Endpoints

#### Upload File
```bash
POST /upload
Content-Type: application/json

{
  "filename": "receipt.jpg",
  "content": "base64-encoded-file-content"
}
```

#### Get Expenses
```bash
GET /expenses

Response:
{
  "expenses": [...],
  "count": 42
}
```

## Data Processing

### Amount Extraction
The system uses multiple regex patterns to extract amounts:
- `Total: $25.50`
- `Amount $45.00`
- `$89.99`
- `15.75`

### Date Parsing
Supports various date formats:
- MM/DD/YYYY
- DD/MM/YYYY
- YYYY-MM-DD
- MM/DD/YY (with century correction)

### Categorization Keywords
- **Food**: restaurant, cafe, food, starbucks, mcdonald
- **Transport**: taxi, uber, bus, train, fuel, gas
- **Office**: office, supplies, computer, software
- **Travel**: hotel, flight, airline, booking
- **Healthcare**: pharmacy, medical, doctor, hospital

## Error Handling

The application includes comprehensive error handling:
- AWS credential expiration with fallback data
- Invalid file format detection
- Amount validation (positive values only)
- Date format validation
- Required field checking
- Individual document failure recovery

## Testing

Run unit tests:
```bash
python -m pytest tests/
```

Or run specific test:
```bash
python tests/test_process_document.py
```

## Monitoring

### CloudWatch Logs
- Lambda function execution logs
- Error tracking and debugging
- Performance metrics

### Cost Optimization
- Serverless pay-per-use pricing
- S3 lifecycle policies for document archival
- DynamoDB on-demand pricing
- Optimized Lambda memory allocation

## Security

- IAM roles with least privilege access
- Input validation and sanitization
- File type validation
- CORS configuration for API endpoints
- Encrypted data storage (S3 and DynamoDB)

## Troubleshooting

### Common Issues

1. **AWS Credential Expiration**
   ```bash
   aws configure
   # or
   aws sso login
   ```

2. **Lambda Deployment Fails**
   - Check IAM permissions
   - Verify role exists: `ExpenseAnalyzerLambdaRole`

3. **No Text Extracted**
   - Verify file format is supported
   - Check image quality and text clarity

4. **API Gateway Errors**
   - Verify CORS configuration
   - Check Lambda function permissions

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export AWS_LAMBDA_LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review CloudWatch logs
3. Open an issue on GitHub

---

**Built with ❤️ using AWS serverless technologies**