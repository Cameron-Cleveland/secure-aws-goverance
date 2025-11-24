#!/usr/bin/env python3
"""
Enable BedRock Model Access Programmatically
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def enable_bedrock_access():
    print("🚀 ENABLING BEDROCK MODEL ACCESS")
    print("=" * 50)
    
    # Try different methods to enable BedRock access
    
    # Method 1: Use AWS CLI via boto3 to call bedrock runtime
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    bedrock = boto3.client('bedrock', region_name='us-east-1')
    
    # Get available models first
    try:
        print("🔍 Checking available models...")
        response = bedrock.list_foundation_models()
        models = response['modelSummaries']
        print(f"Found {len(models)} models in catalog")
        
        # Try to enable access by attempting to invoke a model
        # This often triggers the auto-enablement
        test_models = [
            'amazon.titan-text-express-v1',
            'amazon.titan-text-lite-v1',
            'anthropic.claude-instant-v1',
            'ai21.j2-mid-v1'
        ]
        
        for model_id in test_models:
            print(f"🔄 Attempting to enable {model_id}...")
            try:
                # Try a simple invocation to trigger enablement
                if 'titan' in model_id:
                    body = {
                        "inputText": "test",
                        "textGenerationConfig": {
                            "maxTokenCount": 5,
                            "temperature": 0.1
                        }
                    }
                elif 'claude' in model_id:
                    body = {
                        "prompt": "\n\nHuman: test\n\nAssistant:",
                        "max_tokens_to_sample": 5,
                        "temperature": 0.1
                    }
                else:
                    body = {
                        "prompt": "test",
                        "maxTokens": 5,
                        "temperature": 0.1
                    }
                
                bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body)
                )
                print(f"✅ {model_id} - Access enabled!")
                return True
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if 'AccessDeniedException' in error_code:
                    print(f"❌ {model_id} - Access denied: {e.response['Error']['Message']}")
                elif 'ResourceNotFoundException' in error_code:
                    print(f"❌ {model_id} - Model not found/accessible")
                elif 'ValidationException' in error_code:
                    print(f"❌ {model_id} - Validation error (may need manual enablement)")
                else:
                    print(f"❌ {model_id} - Error: {error_code}")
        
        print("\n🔧 Manual enablement required via AWS Console")
        print("Please follow these steps:")
        print("1. Go to AWS Console → BedRock")
        print("2. Click 'Playground' in the left sidebar")
        print("3. Select any model (e.g., Claude, Titan)")
        print("4. If prompted, complete any verification steps")
        print("5. Try running the test again")
        return False
        
    except ClientError as e:
        print(f"❌ Error accessing BedRock: {e}")
        return False

def check_current_access():
    """Check what access we currently have"""
    print("\n🔍 CHECKING CURRENT BEDROCK ACCESS")
    print("=" * 50)
    
    sts = boto3.client('sts')
    try:
        identity = sts.get_caller_identity()
        print(f"Account: {identity['Account']}")
        print(f"User ARN: {identity['Arn']}")
    except Exception as e:
        print(f"Error getting identity: {e}")
    
    # Check BedRock permissions
    bedrock = boto3.client('bedrock', region_name='us-east-1')
    try:
        response = bedrock.list_foundation_models()
        print(f"Models in catalog: {len(response['modelSummaries'])}")
        
        # Check if we have any invocation permissions
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Try a simple list operation to check basic access
        print("Basic BedRock access: ✅ Available")
        return True
        
    except ClientError as e:
        print(f"Basic BedRock access: ❌ {e.response['Error']['Code']}")
        return False

def main():
    print("🤖 BEDROCK ACCESS CONFIGURATION")
    print("=" * 50)
    
    # First check current access
    has_basic_access = check_current_access()
    
    if has_basic_access:
        print("\n✅ Basic BedRock access is configured")
        print("🔄 Attempting to enable model invocation...")
        success = enable_bedrock_access()
        
        if success:
            print("\n🎉 BEDROCK ACCESS ENABLED SUCCESSFULLY!")
        else:
            print("\n⚠️ Manual intervention required")
            print("Please enable BedRock via AWS Console as shown above")
    else:
        print("\n❌ Basic BedRock access not available")
        print("Please check IAM permissions and ensure BedRock is available in your region")

if __name__ == "__main__":
    main()
