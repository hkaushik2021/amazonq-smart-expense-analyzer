import json
import boto3
import re
import uuid
from datetime import datetime
from decimal import Decimal

def lambda_handler(event, context):
    """Process uploaded documents with Textract and save to DynamoDB"""
    
    try:
        textract = boto3.client('textract')
        dynamodb = boto3.resource('dynamodb')
        s3 = boto3.client('s3')
        table = dynamodb.Table('ExpenseRecords')
    except Exception as e:
        print(f"AWS service initialization error: {e}")
        return {
            'statusCode': 500, 
            'body': json.dumps({'error': f'Service initialization failed: {str(e)}'})
        }
    
    try:
        # Handle missing Records (for manual testing)
        if 'Records' not in event:
            return {'statusCode': 400, 'body': json.dumps({'error': 'No S3 event records found'})}
            
        processed_count = 0
        for record in event['Records']:
            try:
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']
                
                # Skip non-document files
                if not key.lower().endswith(('.txt', '.text', '.pdf', '.jpg', '.jpeg', '.png')):
                    print(f"Skipping unsupported file: {key}")
                    continue
                
                print(f"Processing: {key}")
                
                # Extract text based on file type
                if key.lower().endswith(('.txt', '.text')):
                    obj = s3.get_object(Bucket=bucket, Key=key)
                    full_text = obj['Body'].read().decode('utf-8')
                    print(f"Read text file: {len(full_text)} characters")
                else:
                    response = textract.detect_document_text(
                        Document={'S3Object': {'Bucket': bucket, 'Name': key}}
                    )
                    
                    text_lines = [block['Text'] for block in response['Blocks'] 
                                if block['BlockType'] == 'LINE']
                    full_text = ' '.join(text_lines)
                    print(f"Extracted text: {len(full_text)} characters")
                
                if not full_text.strip():
                    print(f"No text extracted from {key}")
                    continue
                
                # Extract and validate expense information
                expense_data = extract_expense_info(full_text, key)
                if not validate_expense_data(expense_data):
                    print(f"Invalid expense data for {key}")
                    continue
                
                # Save to DynamoDB
                table.put_item(Item=expense_data)
                print(f"Saved expense: {expense_data['expense_id']} - ${expense_data['amount']}")
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing {key}: {str(e)}")
                continue
            
        return {
            'statusCode': 200, 
            'body': json.dumps({
                'message': 'Processing complete',
                'processed_count': processed_count
            })
        }
        
    except Exception as e:
        print(f"Lambda error: {str(e)}")
        return {
            'statusCode': 500, 
            'body': json.dumps({'error': f'Processing failed: {str(e)}'})
        }

def extract_expense_info(text, s3_key):
    """Extract expense information from text"""
    
    # Extract amount with multiple patterns
    amount_patterns = [
        r'Total[:\s]*\$?([0-9]+(?:\.[0-9]{2})?)',
        r'Amount[:\s]*\$?([0-9]+(?:\.[0-9]{2})?)',
        r'\$([0-9]+\.[0-9]{2})',
        r'(?:^|\s)([0-9]+\.[0-9]{2})(?=\s|$)'
    ]
    
    amount = Decimal('0.00')
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                extracted_amount = Decimal(match.group(1))
                if extracted_amount > 0:
                    amount = extracted_amount
                    break
            except (ValueError, ArithmeticError) as e:
                print(f"Amount parsing error: {e}")
                continue
    
    # Categorize expense
    category = categorize_expense(text)
    
    # Extract description
    description = extract_description(text, s3_key)
    
    # Extract date
    expense_date = extract_date(text)
    
    return {
        'expense_id': str(uuid.uuid4()),
        'amount': amount,
        'category': category,
        'description': description,
        'date': expense_date,
        'processed_at': datetime.utcnow().isoformat(),
        's3_key': s3_key,
        'raw_text': text[:500]
    }

def categorize_expense(text):
    """Categorize expense based on keywords"""
    text_lower = text.lower()
    
    categories = {
        'food': ['restaurant', 'cafe', 'food', 'lunch', 'dinner', 'pizza', 'burger', 'starbucks', 'mcdonald', 'subway'],
        'transport': ['taxi', 'uber', 'bus', 'train', 'fuel', 'gas', 'parking', 'metro', 'lyft', 'transport'],
        'office': ['office', 'supplies', 'stationery', 'paper', 'computer', 'software', 'staples', 'depot'],
        'travel': ['hotel', 'flight', 'airline', 'accommodation', 'booking', 'airbnb', 'expedia', 'marriott'],
        'healthcare': ['pharmacy', 'medical', 'doctor', 'hospital', 'clinic', 'cvs', 'walgreens', 'health']
    }
    
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    return 'other'

def extract_description(text, s3_key):
    """Extract meaningful description from text"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Look for business name or meaningful description
    for line in lines:
        if len(line) > 5 and not re.match(r'^\d+[\.\-/]\d+', line):
            return line[:50]
    
    # Fallback to filename
    return s3_key.split('/')[-1].replace('_', ' ')

def extract_date(text):
    """Extract date from text with improved patterns"""
    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2})',
        r'Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            date_formats = ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y']
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    # Handle 2-digit years
                    if parsed_date.year < 1950:
                        parsed_date = parsed_date.replace(year=parsed_date.year + 100)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
    
    return datetime.now().strftime('%Y-%m-%d')

def validate_expense_data(expense_data):
    """Validate extracted expense data"""
    try:
        # Check required fields
        required_fields = ['expense_id', 'amount', 'category', 'description', 'date']
        for field in required_fields:
            if field not in expense_data or not expense_data[field]:
                print(f"Missing or empty field: {field}")
                return False
        
        # Validate amount
        if expense_data['amount'] <= 0:
            print(f"Invalid amount: {expense_data['amount']}")
            return False
        
        # Validate date format
        try:
            datetime.strptime(expense_data['date'], '%Y-%m-%d')
        except ValueError:
            print(f"Invalid date format: {expense_data['date']}")
            return False
        
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False