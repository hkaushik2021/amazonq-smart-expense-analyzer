import json
import boto3
import base64
from datetime import datetime

def lambda_handler(event, context):
    """Handle file uploads to S3 with validation"""
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight requests
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        # Parse request body
        raw_body = event.get('body', '')
        if not raw_body:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Empty request body'})
            }
        
        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid JSON format'})
            }
        
        # Validate required fields
        if 'filename' not in body or 'content' not in body:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing filename or content'})
            }
        
        filename = body['filename']
        file_content = body['content']
        
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.txt', '.text']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'})
            }
        
        # Initialize S3 client
        s3_client = boto3.client('s3')
        bucket_name = 'expense-analyzer-documents'
        
        # Generate unique key
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f"uploads/{timestamp}_{filename}"
        
        # Decode base64 content
        try:
            file_data = base64.b64decode(file_content)
        except Exception as e:
            # Handle plain text content for testing
            if isinstance(file_content, str) and not file_content.startswith('data:'):
                file_data = file_content.encode('utf-8')
            else:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': f'Invalid file content encoding: {str(e)}'})
                }
        
        # Upload to S3
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=file_data,
                ContentType=get_content_type(filename)
            )
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'File uploaded successfully',
                    's3_key': s3_key,
                    'filename': filename
                })
            }
            
        except Exception as e:
            print(f"S3 upload error: {str(e)}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': f'Upload failed: {str(e)}'})
            }
        
    except Exception as e:
        print(f"Upload API error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Request processing failed: {str(e)}'})
        }

def get_content_type(filename):
    """Get content type based on file extension"""
    extension = filename.lower().split('.')[-1]
    content_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'text': 'text/plain'
    }
    return content_types.get(extension, 'application/octet-stream')