#!/usr/bin/env python3
import boto3
import zipfile
import os
import json

def create_lambda_package(function_name):
    """Create deployment package for Lambda function"""
    zip_filename = f"{function_name}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the Lambda function file
        zipf.write(f"backend/{function_name}.py", f"{function_name}.py")
        
        # Add requirements if needed (boto3 is available by default)
        # For production, you might want to include specific versions
    
    print(f"✅ Created deployment package: {zip_filename}")
    return zip_filename

def deploy_lambda_function(function_name, description, handler, memory=256, timeout=30):
    """Deploy Lambda function"""
    lambda_client = boto3.client('lambda')
    iam = boto3.client('iam')
    
    # Get IAM role ARN
    try:
        role_response = iam.get_role(RoleName='ExpenseAnalyzerLambdaRole')
        role_arn = role_response['Role']['Arn']
    except Exception as e:
        print(f"❌ Error getting IAM role: {e}")
        return None
    
    # Create deployment package
    zip_filename = create_lambda_package(function_name)
    
    try:
        # Read the zip file
        with open(zip_filename, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Create or update Lambda function
        try:
            # Try to update existing function
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"✅ Updated Lambda function: {function_name}")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler=handler,
                Code={'ZipFile': zip_content},
                Description=description,
                Timeout=timeout,
                MemorySize=memory,
                Environment={
                    'Variables': {
                        'DYNAMODB_TABLE': 'ExpenseRecords',
                        'S3_BUCKET': 'expense-analyzer-documents'
                    }
                }
            )
            print(f"✅ Created Lambda function: {function_name}")
        
        # Clean up zip file
        os.remove(zip_filename)
        
        return response['FunctionArn']
        
    except Exception as e:
        print(f"❌ Error deploying {function_name}: {e}")
        # Clean up zip file on error
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        return None

def configure_s3_trigger():
    """Configure S3 trigger for process_document function"""
    s3 = boto3.client('s3')
    lambda_client = boto3.client('lambda')
    
    try:
        # Add permission for S3 to invoke Lambda
        try:
            lambda_client.add_permission(
                FunctionName='process_document',
                StatementId='s3-trigger',
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn='arn:aws:s3:::expense-analyzer-documents'
            )
            print("✅ Added S3 permission to process_document")
        except Exception as e:
            if 'ResourceConflictException' in str(e):
                print("✅ S3 permission already exists for process_document")
            else:
                raise
        
        # Configure S3 notification
        notification_config = {
            'LambdaFunctionConfigurations': [
                {
                    'Id': 'process-document-trigger',
                    'LambdaFunctionArn': f'arn:aws:lambda:{boto3.Session().region_name}:{boto3.client("sts").get_caller_identity()["Account"]}:function:process_document',
                    'Events': ['s3:ObjectCreated:*'],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {
                                    'Name': 'prefix',
                                    'Value': 'uploads/'
                                }
                            ]
                        }
                    }
                }
            ]
        }
        
        s3.put_bucket_notification_configuration(
            Bucket='expense-analyzer-documents',
            NotificationConfiguration=notification_config
        )
        
        print("✅ Configured S3 trigger for process_document")
        
    except Exception as e:
        print(f"❌ Error configuring S3 trigger: {e}")

def configure_api_gateway_integration():
    """Configure API Gateway integration with Lambda functions"""
    apigateway = boto3.client('apigateway')
    
    try:
        # Find the API
        apis = apigateway.get_rest_apis()
        api_id = None
        
        for api in apis['items']:
            if 'expense' in api['name'].lower():
                api_id = api['id']
                break
        
        if not api_id:
            print("❌ No expense analyzer API found")
            return None
        
        print(f"Found API: {api_id}")
        
        # Get resources
        resources = apigateway.get_resources(restApiId=api_id)
        
        upload_resource_id = None
        expenses_resource_id = None
        
        for resource in resources['items']:
            if resource.get('pathPart') == 'upload':
                upload_resource_id = resource['id']
            elif resource.get('pathPart') == 'expenses':
                expenses_resource_id = resource['id']
        
        region = boto3.Session().region_name or 'us-east-1'
        account_id = boto3.client('sts').get_caller_identity()['Account']
        
        # Configure upload endpoint
        if upload_resource_id:
            try:
                # Delete existing methods
                for method in ['POST', 'OPTIONS']:
                    try:
                        apigateway.delete_method(
                            restApiId=api_id,
                            resourceId=upload_resource_id,
                            httpMethod=method
                        )
                    except:
                        pass
                
                # Add OPTIONS method for CORS
                apigateway.put_method(
                    restApiId=api_id,
                    resourceId=upload_resource_id,
                    httpMethod='OPTIONS',
                    authorizationType='NONE'
                )
                
                apigateway.put_method_response(
                    restApiId=api_id,
                    resourceId=upload_resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Origin': False,
                        'method.response.header.Access-Control-Allow-Headers': False,
                        'method.response.header.Access-Control-Allow-Methods': False
                    }
                )
                
                apigateway.put_integration(
                    restApiId=api_id,
                    resourceId=upload_resource_id,
                    httpMethod='OPTIONS',
                    type='MOCK',
                    requestTemplates={'application/json': '{"statusCode": 200}'}
                )
                
                apigateway.put_integration_response(
                    restApiId=api_id,
                    resourceId=upload_resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'",
                        'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                        'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'"
                    }
                )
                
                # Add POST method
                apigateway.put_method(
                    restApiId=api_id,
                    resourceId=upload_resource_id,
                    httpMethod='POST',
                    authorizationType='NONE'
                )
                
                apigateway.put_method_response(
                    restApiId=api_id,
                    resourceId=upload_resource_id,
                    httpMethod='POST',
                    statusCode='200'
                )
                
                upload_lambda_arn = f"arn:aws:lambda:{region}:{account_id}:function:upload_api"
                apigateway.put_integration(
                    restApiId=api_id,
                    resourceId=upload_resource_id,
                    httpMethod='POST',
                    type='AWS_PROXY',
                    integrationHttpMethod='POST',
                    uri=f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{upload_lambda_arn}/invocations"
                )
                
                apigateway.put_integration_response(
                    restApiId=api_id,
                    resourceId=upload_resource_id,
                    httpMethod='POST',
                    statusCode='200'
                )
                
                print("✅ Configured POST /upload with CORS")
            except Exception as e:
                print(f"⚠️ Upload method error: {e}")
        
        # Configure expenses endpoint
        if expenses_resource_id:
            try:
                # Delete existing methods
                for method in ['GET', 'OPTIONS']:
                    try:
                        apigateway.delete_method(
                            restApiId=api_id,
                            resourceId=expenses_resource_id,
                            httpMethod=method
                        )
                    except:
                        pass
                
                # Add OPTIONS method for CORS
                apigateway.put_method(
                    restApiId=api_id,
                    resourceId=expenses_resource_id,
                    httpMethod='OPTIONS',
                    authorizationType='NONE'
                )
                
                apigateway.put_method_response(
                    restApiId=api_id,
                    resourceId=expenses_resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Origin': False,
                        'method.response.header.Access-Control-Allow-Headers': False,
                        'method.response.header.Access-Control-Allow-Methods': False
                    }
                )
                
                apigateway.put_integration(
                    restApiId=api_id,
                    resourceId=expenses_resource_id,
                    httpMethod='OPTIONS',
                    type='MOCK',
                    requestTemplates={'application/json': '{"statusCode": 200}'}
                )
                
                apigateway.put_integration_response(
                    restApiId=api_id,
                    resourceId=expenses_resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'",
                        'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                        'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'"
                    }
                )
                
                # Add GET method
                apigateway.put_method(
                    restApiId=api_id,
                    resourceId=expenses_resource_id,
                    httpMethod='GET',
                    authorizationType='NONE'
                )
                
                apigateway.put_method_response(
                    restApiId=api_id,
                    resourceId=expenses_resource_id,
                    httpMethod='GET',
                    statusCode='200'
                )
                
                expenses_lambda_arn = f"arn:aws:lambda:{region}:{account_id}:function:get_expenses"
                apigateway.put_integration(
                    restApiId=api_id,
                    resourceId=expenses_resource_id,
                    httpMethod='GET',
                    type='AWS_PROXY',
                    integrationHttpMethod='POST',
                    uri=f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{expenses_lambda_arn}/invocations"
                )
                
                apigateway.put_integration_response(
                    restApiId=api_id,
                    resourceId=expenses_resource_id,
                    httpMethod='GET',
                    statusCode='200'
                )
                
                print("✅ Configured GET /expenses with CORS")
            except Exception as e:
                print(f"⚠️ Expenses method error: {e}")
        
        # Deploy API
        try:
            apigateway.create_deployment(
                restApiId=api_id,
                stageName='prod',
                description='Fixed API Gateway methods'
            )
            print("✅ Deployed API Gateway")
        except Exception as e:
            print(f"⚠️ Deployment warning: {e}")
        
        # Get API URL
        api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"
        print(f"📋 API Gateway URL: {api_url}")
        
        return api_url
        
    except Exception as e:
        print(f"❌ Error configuring API Gateway: {e}")
        return None

def add_api_gateway_permissions():
    """Add API Gateway permissions to Lambda functions"""
    lambda_client = boto3.client('lambda')
    apigateway = boto3.client('apigateway')
    region = boto3.Session().region_name or 'us-east-1'
    account_id = boto3.client('sts').get_caller_identity()['Account']
    
    # Find the API ID
    apis = apigateway.get_rest_apis()
    api_id = None
    for api in apis['items']:
        if 'expense' in api['name'].lower():
            api_id = api['id']
            break
    
    if not api_id:
        print("❌ No expense analyzer API found")
        return
    
    api_functions = ['get_expenses', 'upload_api']
    
    for func_name in api_functions:
        try:
            # Remove existing permission first
            try:
                lambda_client.remove_permission(
                    FunctionName=func_name,
                    StatementId=f'api-gateway-invoke-{func_name}'
                )
            except:
                pass
            
            # Add new permission with specific API ID
            lambda_client.add_permission(
                FunctionName=func_name,
                StatementId=f'api-gateway-invoke-{func_name}',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f'arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*'
            )
            print(f"✅ Added API Gateway permission to {func_name}")
        except Exception as e:
            if 'ResourceConflictException' in str(e):
                print(f"✅ API Gateway permission already exists for {func_name}")
            else:
                print(f"❌ Error adding permission to {func_name}: {e}")

def main():
    """Deploy all Lambda functions"""
    print("Starting Lambda deployment...")
    
    # Deploy Lambda functions
    functions = [
        {
            'name': 'process_document',
            'description': 'Process uploaded documents with Textract',
            'handler': 'process_document.lambda_handler',
            'memory': 512,
            'timeout': 300
        },
        {
            'name': 'get_expenses',
            'description': 'Get expenses from DynamoDB',
            'handler': 'get_expenses.lambda_handler',
            'memory': 256,
            'timeout': 30
        },
        {
            'name': 'upload_api',
            'description': 'Handle file uploads to S3',
            'handler': 'upload_api.lambda_handler',
            'memory': 256,
            'timeout': 60
        }
    ]
    
    deployed_functions = []
    
    for func in functions:
        print(f"\nDeploying {func['name']}...")
        arn = deploy_lambda_function(
            func['name'],
            func['description'],
            func['handler'],
            func['memory'],
            func['timeout']
        )
        
        if arn:
            deployed_functions.append(func['name'])
    
    # Configure API Gateway first
    print("\nConfiguring API Gateway...")
    api_url = configure_api_gateway_integration()
    
    # Add API Gateway permissions
    print("\nAdding API Gateway permissions...")
    add_api_gateway_permissions()
    
    # Configure S3 trigger
    if 'process_document' in deployed_functions:
        print("\nConfiguring S3 trigger...")
        configure_s3_trigger()
    
    print(f"\nLambda deployment complete!")
    print(f"Deployed functions: {', '.join(deployed_functions)}")
    
    # Test API endpoints
    print(f"\nAPI Gateway configuration complete!")
    if api_url:
        print(f"Your API is at: {api_url}")
    print(f"\nRun: python test_deployment.py to verify")

if __name__ == '__main__':
    main()