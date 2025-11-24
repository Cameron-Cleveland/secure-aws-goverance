#!/usr/bin/env python3
"""
Manual AWS Resource Discovery
"""

import boto3
import json

def discover_resources():
    print("🔍 MANUAL AWS RESOURCE DISCOVERY")
    print("=" * 60)
    
    # S3 Resources
    print("\n🪣 S3 BUCKETS:")
    s3 = boto3.client('s3')
    try:
        response = s3.list_buckets()
        for bucket in response['Buckets']:
            if 'secure-governance' in bucket['Name'] or 'hr-documents' in bucket['Name']:
                print(f"  ✅ {bucket['Name']} (Created: {bucket['CreationDate'].strftime('%Y-%m-%d')})")
    except Exception as e:
        print(f"  ❌ Error listing buckets: {e}")
    
    # IAM Roles
    print("\n👤 IAM ROLES:")
    iam = boto3.client('iam')
    try:
        response = iam.list_roles(MaxItems=50)
        for role in response['Roles']:
            if 'secure-governance' in role['RoleName'] or 'hr-workflow' in role['RoleName']:
                print(f"  ✅ {role['RoleName']} (Created: {role['CreateDate'].strftime('%Y-%m-%d')})")
    except Exception as e:
        print(f"  ❌ Error listing roles: {e}")
    
    # BedRock Models
    print("\n🤖 BEDROCK MODELS:")
    bedrock = boto3.client('bedrock', region_name='us-east-1')
    try:
        response = bedrock.list_foundation_models()
        active_models = [m for m in response['modelSummaries'] if m['modelLifecycle'].get('status') == 'ACTIVE']
        text_models = [m for m in active_models if 'TEXT' in m['outputModalities']]
        
        print(f"  Total Active Models: {len(active_models)}")
        print(f"  Text Models: {len(text_models)}")
        
        # Show some available text models
        for model in text_models[:5]:  # Show first 5
            print(f"  ✅ {model['modelId']}")
            
    except Exception as e:
        print(f"  ❌ Error listing models: {e}")
    
    # Lambda Functions
    print("\n⚡ LAMBDA FUNCTIONS:")
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    try:
        response = lambda_client.list_functions(MaxItems=50)
        for function in response['Functions']:
            if 'secure-governance' in function['FunctionName'] or 'hr-onboarding' in function['FunctionName']:
                print(f"  ✅ {function['FunctionName']} (Runtime: {function['Runtime']})")
    except Exception as e:
        print(f"  ❌ Error listing functions: {e}")

if __name__ == "__main__":
    discover_resources()
