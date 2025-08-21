import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    """Get expenses from DynamoDB with CORS support"""
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight requests
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('ExpenseRecords')
        
        # Scan all expenses
        response = table.scan()
        expenses = response['Items']
        
        # Convert Decimal to float for JSON serialization
        for expense in expenses:
            if 'amount' in expense:
                expense['amount'] = float(expense['amount'])
        
        # Sort by date descending
        expenses.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'expenses': expenses,
                'count': len(expenses)
            })
        }
        
    except Exception as e:
        print(f"Error retrieving expenses: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Failed to retrieve expenses: {str(e)}'})
        }