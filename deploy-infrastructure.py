#!/usr/bin/env python3
import boto3
import json
import time

def create_s3_buckets():
    """Create S3 buckets for documents and frontend"""
    s3 = boto3.client('s3')
    
    buckets = [
        'expense-analyzer-documents',
        'expense-analyzer-frontend'
    ]
    
    for bucket_name in buckets:
        try:
            s3.create_bucket(Bucket=bucket_name)
            print(f"✅ Created S3 bucket: {bucket_name}")
            
            # Enable versioning for documents bucket
            if 'documents' in bucket_name:
                s3.put_bucket_versioning(
                    Bucket=bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
                print(f"✅ Enabled versioning for {bucket_name}")
            
            # Configure website hosting for frontend bucket
            if 'frontend' in bucket_name:
                try:
                    # First try to disable block public access
                    try:
                        s3.put_public_access_block(
                            Bucket=bucket_name,
                            PublicAccessBlockConfiguration={
                                'BlockPublicAcls': False,
                                'IgnorePublicAcls': False,
                                'BlockPublicPolicy': False,
                                'RestrictPublicBuckets': False
                            }
                        )
                        print(f"✅ Disabled block public access for {bucket_name}")
                    except Exception as block_e:
                        print(f"⚠️  Could not disable block public access: {block_e}")
                    
                    # Configure website hosting
                    s3.put_bucket_website(
                        Bucket=bucket_name,
                        WebsiteConfiguration={
                            'IndexDocument': {'Suffix': 'index.html'},
                            'ErrorDocument': {'Key': 'error.html'}
                        }
                    )
                    print(f"✅ Configured website hosting for {bucket_name}")
                    
                    # Set public read policy
                    policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "PublicReadGetObject",
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": "s3:GetObject",
                                "Resource": f"arn:aws:s3:::{bucket_name}/*"
                            }
                        ]
                    }
                    
                    try:
                        s3.put_bucket_policy(
                            Bucket=bucket_name,
                            Policy=json.dumps(policy)
                        )
                        print(f"✅ Set public read policy for {bucket_name}")
                    except Exception as policy_e:
                        print(f"⚠️  Could not set public policy: {policy_e}")
                        print(f"ℹ️  Manually set bucket policy for public read access")
                        
                except Exception as e:
                    print(f"⚠️  Website hosting config failed for {bucket_name}: {e}")
                
        except Exception as e:
            if 'BucketAlreadyOwnedByYou' in str(e):
                print(f"ℹ️  Bucket {bucket_name} already exists")
            else:
                print(f"❌ Error creating bucket {bucket_name}: {e}")

def create_dynamodb_table():
    """Create DynamoDB table for expense records"""
    dynamodb = boto3.resource('dynamodb')
    
    try:
        table = dynamodb.create_table(
            TableName='ExpenseRecords',
            KeySchema=[
                {
                    'AttributeName': 'expense_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'expense_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        print("✅ Created DynamoDB table: ExpenseRecords")
        
    except Exception as e:
        if 'ResourceInUseException' in str(e):
            print("ℹ️  DynamoDB table ExpenseRecords already exists")
        else:
            print(f"❌ Error creating DynamoDB table: {e}")

def create_iam_roles():
    """Create IAM roles for Lambda functions"""
    iam = boto3.client('iam')
    
    # Lambda execution role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Policy for Lambda functions
    lambda_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": "arn:aws:s3:::expense-analyzer-documents/*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:Scan",
                    "dynamodb:Query"
                ],
                "Resource": "arn:aws:dynamodb:*:*:table/ExpenseRecords"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "textract:DetectDocumentText"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Create role
        iam.create_role(
            RoleName='ExpenseAnalyzerLambdaRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Expense Analyzer Lambda functions'
        )
        
        # Attach policy
        iam.put_role_policy(
            RoleName='ExpenseAnalyzerLambdaRole',
            PolicyName='ExpenseAnalyzerLambdaPolicy',
            PolicyDocument=json.dumps(lambda_policy)
        )
        
        print("✅ Created IAM role: ExpenseAnalyzerLambdaRole")
        
        # Wait for role to propagate
        time.sleep(10)
        
    except Exception as e:
        if 'EntityAlreadyExists' in str(e):
            print("ℹ️  IAM role ExpenseAnalyzerLambdaRole already exists")
            # Update policy
            try:
                iam.put_role_policy(
                    RoleName='ExpenseAnalyzerLambdaRole',
                    PolicyName='ExpenseAnalyzerLambdaPolicy',
                    PolicyDocument=json.dumps(lambda_policy)
                )
                print("✅ Updated IAM role policy")
            except Exception as update_e:
                print(f"⚠️  Error updating IAM policy: {update_e}")
        else:
            print(f"❌ Error creating IAM role: {e}")

def create_api_gateway():
    """Create API Gateway for REST endpoints"""
    apigateway = boto3.client('apigateway')
    
    try:
        # Check if API already exists
        apis = apigateway.get_rest_apis()
        existing_api = None
        
        for api in apis['items']:
            if api['name'] == 'expense-analyzer-api':
                existing_api = api
                break
        
        if existing_api:
            api_id = existing_api['id']
            print(f"ℹ️  API Gateway already exists: {api_id}")
        else:
            # Create REST API
            api = apigateway.create_rest_api(
                name='expense-analyzer-api',
                description='API for Smart Expense Analyzer',
                endpointConfiguration={
                    'types': ['REGIONAL']
                }
            )
            
            api_id = api['id']
            print(f"✅ Created API Gateway: {api_id}")
            
            # Get root resource
            resources = apigateway.get_resources(restApiId=api_id)
            root_id = resources['items'][0]['id']
            
            # Create resources
            try:
                upload_resource = apigateway.create_resource(
                    restApiId=api_id,
                    parentId=root_id,
                    pathPart='upload'
                )
                
                expenses_resource = apigateway.create_resource(
                    restApiId=api_id,
                    parentId=root_id,
                    pathPart='expenses'
                )
                
                print("✅ Created API Gateway resources")
            except Exception as resource_e:
                print(f"⚠️  Error creating API resources: {resource_e}")
        
        return api_id
        
    except Exception as e:
        print(f"❌ Error with API Gateway: {e}")
        return None

def fix_api_permissions():
    """Fix Lambda permissions for API Gateway"""
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
        return False
    
    print(f"Found API: {api_id}")
    
    api_functions = ['get_expenses', 'upload_api']
    
    for func_name in api_functions:
        try:
            # Remove existing permissions
            try:
                lambda_client.remove_permission(
                    FunctionName=func_name,
                    StatementId=f'api-gateway-invoke-{func_name}'
                )
            except:
                pass
            
            # Add new permission
            lambda_client.add_permission(
                FunctionName=func_name,
                StatementId=f'api-gateway-invoke-{func_name}',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f'arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*'
            )
            print(f"✅ Fixed permission for {func_name}")
            
        except Exception as e:
            print(f"❌ Error fixing {func_name}: {e}")
            return False
    
    # Redeploy API
    try:
        apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Fixed Lambda permissions'
        )
        print("✅ Redeployed API Gateway")
        
        api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"
        print(f"📋 API URL: {api_url}")
        return True
        
    except Exception as e:
        print(f"❌ Error redeploying API: {e}")
        return False

def main():
    """Deploy all infrastructure components"""
    print("🚀 Starting infrastructure deployment...")
    
    print("\n📦 Creating S3 buckets...")
    create_s3_buckets()
    
    print("\n🗄️  Creating DynamoDB table...")
    create_dynamodb_table()
    
    print("\n🔐 Creating IAM roles...")
    create_iam_roles()
    
    print("\n🌐 Creating API Gateway...")
    api_id = create_api_gateway()
    
    print("\n✅ Infrastructure deployment complete!")
    
    if api_id:
        print(f"\n📋 Next steps:")
        print(f"1. Deploy Lambda functions using deploy-lambdas.py")
        print(f"2. Configure API Gateway endpoints")
        print(f"3. Update frontend with API Gateway URL")
        print(f"\nAPI Gateway ID: {api_id}")
        print(f"\nTo fix API permissions later, run: python deploy-infrastructure.py --fix-permissions")

def fix_permissions_only():
    """Fix API permissions only"""
    print("🔧 Fixing API Gateway permissions...")
    if fix_api_permissions():
        print("\n✅ API Gateway permissions fixed!")
        print("Test your endpoints now:")
        print("GET /expenses and POST /upload should work")
    else:
        print("\n❌ Failed to fix permissions")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--fix-permissions':
        fix_permissions_only()
    else:
        main()