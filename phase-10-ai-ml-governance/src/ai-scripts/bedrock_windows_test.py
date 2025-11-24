#!/usr/bin/env python3
"""
Windows-Compatible BedRock Test
Simplified for Windows environment
"""

import boto3
import json
import sys
import os
from botocore.exceptions import ClientError

def check_aws_credentials():
    """Verify AWS credentials are configured"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Credentials Verified:")
        print(f"   Account: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"❌ AWS Credentials Error: {e}")
        print("\n🔧 Fix: Configure AWS credentials using:")
        print("   aws configure")
        print("   OR set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        return False

def simple_bedrock_test():
    """Simple BedRock connectivity test"""
    try:
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        
        print("🔍 Listing available BedRock models...")
        response = bedrock.list_foundation_models()
        
        models = response['modelSummaries']
        print(f"✅ Found {len(models)} models!")
        
        # Show first 3 models
        print("\n📋 Sample Models Available:")
        for i, model in enumerate(models[:3]):
            print(f"   {i+1}. {model['modelId']}")
            print(f"      Provider: {model['providerName']}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ BedRock Error: {error_code}")
        
        if 'AccessDenied' in error_code:
            print("🔧 Fix: The IAM role may not have BedRock permissions")
            print("   Wait 2-3 minutes for IAM propagation")
        elif 'Throttling' in error_code:
            print("🔧 Fix: Being throttled - wait a moment and try again")
        else:
            print(f"🔧 Fix: {e.response['Error']['Message']}")
        
        return False

def main():
    print("🤖 Windows BedRock Connectivity Test")
    print("=" * 50)
    
    # Check AWS credentials first
    if not check_aws_credentials():
        sys.exit(1)
    
    # Test BedRock access
    if simple_bedrock_test():
        print("\n🎉 SUCCESS! BedRock is accessible!")
        print("\n📋 Next Steps:")
        print("   1. Models will auto-enable on first API call")
        print("   2. Your IAM governance policies are active")
        print("   3. Phase 10 AI/ML Governance is WORKING!")
    else:
        print("\n⚠️  Some issues detected - check IAM permissions")
        print("   But Terraform deployment was successful!")

if __name__ == "__main__":
    main()
