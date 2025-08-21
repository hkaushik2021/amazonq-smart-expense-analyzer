#!/usr/bin/env python3
"""
Deployment Verification Test Suite
Tests all components of the Smart Expense Analyzer to ensure proper deployment
"""

import boto3
import json
import requests
import base64
import time
from decimal import Decimal

def test_s3_buckets():
    """Test S3 bucket creation and configuration"""
    print("Testing S3 buckets...")
    s3 = boto3.client('s3')
    
    buckets = ['expense-analyzer-documents', 'expense-analyzer-frontend']
    results = []
    
    for bucket in buckets:
        try:
            # Check if bucket exists
            s3.head_bucket(Bucket=bucket)
            print(f"  ✓ Bucket {bucket} exists")
            
            # Check website configuration for frontend bucket
            if 'frontend' in bucket:
                try:
                    website_config = s3.get_bucket_website(Bucket=bucket)
                    print(f"  ✓ Website hosting configured for {bucket}")
                except:
                    print(f"  ✗ Website hosting not configured for {bucket}")
                    results.append(False)
                    continue
            
            results.append(True)
            
        except Exception as e:
            print(f"  ✗ Bucket {bucket} error: {e}")
            results.append(False)
    
    return all(results)

def test_dynamodb_table():
    """Test DynamoDB table creation and access"""
    print("Testing DynamoDB table...")
    
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('ExpenseRecords')
        
        # Check table status
        table.load()
        print(f"  ✓ Table ExpenseRecords exists (Status: {table.table_status})")
        
        # Test scan operation
        response = table.scan(Limit=1)
        print(f"  ✓ Table scan successful ({len(response.get('Items', []))} items)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ DynamoDB table error: {e}")
        return False

def test_iam_roles():
    """Test IAM role creation and policies"""
    print("Testing IAM roles...")
    
    try:
        iam = boto3.client('iam')
        
        # Check if role exists
        role = iam.get_role(RoleName='ExpenseAnalyzerLambdaRole')
        print(f"  ✓ IAM role ExpenseAnalyzerLambdaRole exists")
        
        # Check attached policies
        policies = iam.list_role_policies(RoleName='ExpenseAnalyzerLambdaRole')
        if 'ExpenseAnalyzerLambdaPolicy' in policies['PolicyNames']:
            print(f"  ✓ Lambda policy attached")
        else:
            print(f"  ✗ Lambda policy not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ IAM role error: {e}")
        return False

def test_lambda_functions():
    """Test Lambda function deployment"""
    print("Testing Lambda functions...")
    
    lambda_client = boto3.client('lambda')
    functions = ['process_document', 'get_expenses', 'upload_api']
    results = []
    
    for func_name in functions:
        try:
            # Check if function exists
            response = lambda_client.get_function(FunctionName=func_name)
            print(f"  ✓ Lambda function {func_name} exists")
            
            # Check function configuration
            config = response['Configuration']
            print(f"    Runtime: {config['Runtime']}")
            print(f"    Memory: {config['MemorySize']}MB")
            print(f"    Timeout: {config['Timeout']}s")
            
            results.append(True)
            
        except Exception as e:
            print(f"  ✗ Lambda function {func_name} error: {e}")
            results.append(False)
    
    return all(results)

def test_api_gateway():
    """Test API Gateway deployment"""
    print("Testing API Gateway...")
    
    try:
        apigateway = boto3.client('apigateway')
        
        # Get APIs
        apis = apigateway.get_rest_apis()
        
        expense_api = None
        for api in apis['items']:
            if api['name'] == 'expense-analyzer-api':
                expense_api = api
                break
        
        if expense_api:
            api_id = expense_api['id']
            print(f"  ✓ API Gateway exists (ID: {api_id})")
            
            # Check resources
            resources = apigateway.get_resources(restApiId=api_id)
            resource_paths = [r.get('pathPart', '/') for r in resources['items']]
            
            if 'upload' in resource_paths and 'expenses' in resource_paths:
                print(f"  ✓ API resources configured")
            else:
                print(f"  ✗ API resources missing")
                return False
            
            # Get API URL
            region = boto3.Session().region_name or 'us-east-1'
            api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"
            print(f"  ✓ API URL: {api_url}")
            
            return True
        else:
            print(f"  ✗ API Gateway not found")
            return False
            
    except Exception as e:
        print(f"  ✗ API Gateway error: {e}")
        return False

def test_frontend_website():
    """Test frontend website accessibility"""
    print("Testing frontend website...")
    
    try:
        region = boto3.Session().region_name or 'us-east-1'
        website_url = f'http://expense-analyzer-frontend.s3-website-{region}.amazonaws.com'
        
        # Test website accessibility
        response = requests.get(website_url, timeout=10)
        
        if response.status_code == 200:
            print(f"  ✓ Frontend website accessible")
            print(f"  ✓ Website URL: {website_url}")
            
            # Check if it contains expected content
            if 'Smart Expense Analyzer' in response.text:
                print(f"  ✓ Website content verified")
                return True
            else:
                print(f"  ✗ Website content invalid")
                return False
        else:
            print(f"  ✗ Website not accessible (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"  ✗ Frontend website error: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints functionality"""
    print("Testing API endpoints...")
    
    try:
        # Get API Gateway URL
        apigateway = boto3.client('apigateway')
        apis = apigateway.get_rest_apis()
        
        api_id = None
        for api in apis['items']:
            if 'expense' in api['name'].lower():
                api_id = api['id']
                print(f"  Found API: {api['name']} ({api_id})")
                break
        
        if not api_id:
            print(f"  ✗ No expense analyzer API found")
            debug_api_issue()
            return False
        
        region = boto3.Session().region_name or 'us-east-1'
        base_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"
        print(f"  Testing: {base_url}")
        
        # Test GET /expenses endpoint
        try:
            response = requests.get(f"{base_url}/expenses", timeout=10)
            if response.status_code == 200:
                print(f"  ✓ GET /expenses endpoint working")
                data = response.json()
                print(f"    Found {len(data.get('expenses', []))} expenses")
                
                # Test POST /upload endpoint
                test_upload_success = test_upload_endpoint(base_url)
                return test_upload_success
            else:
                print(f"  ✗ GET /expenses failed (Status: {response.status_code})")
                print(f"    Response: {response.text[:200]}")
                debug_api_issue()
                return False
        except Exception as e:
            print(f"  ✗ GET /expenses error: {e}")
            debug_api_issue()
            return False
        
    except Exception as e:
        print(f"  ✗ API endpoints error: {e}")
        return False

def test_upload_endpoint(base_url):
    """Test POST /upload endpoint"""
    try:
        import base64
        
        # Create test file content
        test_content = "Test receipt content for expense analyzer"
        encoded_content = base64.b64encode(test_content.encode()).decode()
        
        # Send JSON payload
        payload = {
            "filename": "test_receipt.txt",
            "content": encoded_content
        }
        
        response = requests.post(
            f"{base_url}/upload",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✓ POST /upload endpoint working")
            return True
        else:
            print(f"  ✗ POST /upload failed (Status: {response.status_code})")
            print(f"    Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ✗ POST /upload error: {e}")
        return False

def debug_api_issue():
    """Debug API Gateway issues"""
    print("\n  === API DEBUG INFO ===")
    try:
        # Check Lambda functions
        lambda_client = boto3.client('lambda')
        functions = ['get_expenses', 'upload_api']
        
        missing_functions = []
        for func_name in functions:
            try:
                response = lambda_client.get_function(FunctionName=func_name)
                print(f"  ✓ {func_name}: {response['Configuration']['State']}")
            except lambda_client.exceptions.ResourceNotFoundException:
                print(f"  ✗ {func_name}: NOT FOUND")
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"  💡 Run: python deploy-lambdas.py")
            return
        
        # Check API Gateway permissions
        region = boto3.Session().region_name or 'us-east-1'
        account_id = boto3.client('sts').get_caller_identity()['Account']
        
        print(f"  Checking Lambda permissions...")
        for func_name in functions:
            try:
                policy = lambda_client.get_policy(FunctionName=func_name)
                if 'apigateway.amazonaws.com' in policy['Policy']:
                    print(f"  ✓ {func_name} has API Gateway permission")
                else:
                    print(f"  ✗ {func_name} missing API Gateway permission")
                    fix_lambda_permissions(func_name, region, account_id)
            except:
                print(f"  ✗ {func_name} has no policy")
                fix_lambda_permissions(func_name, region, account_id)
        
    except Exception as e:
        print(f"  Debug error: {e}")

def fix_lambda_permissions(func_name, region, account_id):
    """Fix Lambda permissions for API Gateway"""
    try:
        lambda_client = boto3.client('lambda')
        lambda_client.add_permission(
            FunctionName=func_name,
            StatementId=f'api-gateway-invoke-{func_name}',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:{region}:{account_id}:*/prod/*'
        )
        print(f"  ✓ Fixed permission for {func_name}")
    except Exception as e:
        if 'ResourceConflictException' in str(e):
            print(f"  ✓ Permission already exists for {func_name}")
        else:
            print(f"  ✗ Failed to fix {func_name}: {e}")

def test_data_processing():
    """Test data processing functionality"""
    print("Testing data processing...")
    
    try:
        # Import processing functions
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from process_document import (
            extract_expense_info,
            categorize_expense,
            validate_expense_data
        )
        
        # Test amount extraction
        test_text = "Starbucks Coffee\nTotal: $4.85\nDate: 01/15/2024"
        result = extract_expense_info(test_text, "test_receipt.jpg")
        
        if result['amount'] == Decimal('4.85'):
            print(f"  ✓ Amount extraction working")
        else:
            print(f"  ✗ Amount extraction failed")
            return False
        
        # Test categorization
        if result['category'] == 'food':
            print(f"  ✓ Categorization working")
        else:
            print(f"  ✗ Categorization failed")
            return False
        
        # Test validation
        if validate_expense_data(result):
            print(f"  ✓ Data validation working")
        else:
            print(f"  ✗ Data validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Data processing error: {e}")
        return False

def run_all_tests():
    """Run all deployment verification tests"""
    print("=" * 50)
    print("SMART EXPENSE ANALYZER - DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("S3 Buckets", test_s3_buckets),
        ("DynamoDB Table", test_dynamodb_table),
        ("IAM Roles", test_iam_roles),
        ("Lambda Functions", test_lambda_functions),
        ("API Gateway", test_api_gateway),
        ("Frontend Website", test_frontend_website),
        ("API Endpoints", test_api_endpoints),
        ("Data Processing", test_data_processing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("DEPLOYMENT VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - DEPLOYMENT SUCCESSFUL!")
        print("\nYour Smart Expense Analyzer is ready to use!")
        
        # Provide access URLs
        region = boto3.Session().region_name or 'us-east-1'
        print(f"\n📱 Frontend URL: http://expense-analyzer-frontend.s3-website-{region}.amazonaws.com")
        
        try:
            apigateway = boto3.client('apigateway')
            apis = apigateway.get_rest_apis()
            for api in apis['items']:
                if 'expense' in api['name'].lower():
                    api_id = api['id']
                    api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"
                    print(f"🔗 API URL: {api_url}")
                    print(f"\n📝 Test your API:")
                    print(f"   GET {api_url}/expenses")
                    print(f"   POST {api_url}/upload")
                    break
        except:
            pass
            
    else:
        print(f"\n❌ {failed} TESTS FAILED - DEPLOYMENT INCOMPLETE")
        print("\n💡 Quick fixes:")
        print("   - Run: python deploy-infrastructure.py")
        print("   - Run: python deploy-lambdas.py")
        print("   - Run: python test_deployment.py (to verify)")
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)