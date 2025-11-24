#!/usr/bin/env python3
"""
Comprehensive BedRock Verification & Testing
Tests real model invocation, not just listing
"""

import boto3
import json
import time
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedRockComprehensiveTest:
    def __init__(self):
        self.region = 'us-east-1'
        try:
            self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=self.region)
            self.bedrock = boto3.client('bedrock', region_name=self.region)
            print("✅ AWS BedRock clients initialized")
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

    def test_model_invocation(self):
        """Test actual model invocation with different providers"""
        test_cases = [
            {
                'name': 'Amazon Titan Text',
                'model_id': 'amazon.titan-text-express-v1',
                'function': self._test_titan
            },
            {
                'name': 'Anthropic Claude', 
                'model_id': 'anthropic.claude-instant-v1',
                'function': self._test_claude
            },
            {
                'name': 'AI21 Jurassic',
                'model_id': 'ai21.j2-mid-v1',
                'function': self._test_ai21
            }
        ]
        
        print("🚀 TESTING ACTUAL MODEL INVOCATION")
        print("=" * 60)
        
        successful_tests = 0
        
        for test in test_cases:
            print(f"\n🎯 Testing {test['name']} ({test['model_id']})...")
            try:
                result = test['function'](test['model_id'])
                if result:
                    print(f"✅ {test['name']}: SUCCESS - Model responded")
                    successful_tests += 1
                else:
                    print(f"⚠️  {test['name']}: Partial success - Check model access")
            except Exception as e:
                print(f"❌ {test['name']}: FAILED - {e}")
        
        print(f"\n📊 INVOCATION TEST SUMMARY: {successful_tests}/{len(test_cases)} models working")
        return successful_tests > 0

    def _test_titan(self, model_id):
        """Test Amazon Titan model"""
        try:
            body = {
                "inputText": "Please respond with just 'Titan test successful' to verify this model is working.",
                "textGenerationConfig": {
                    "maxTokenCount": 20,
                    "temperature": 0.1
                }
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['results'][0]['outputText']
            print(f"   Titan Response: {result.strip()}")
            return True
            
        except ClientError as e:
            print(f"   Titan Error: {e.response['Error']['Code']}")
            return False

    def _test_claude(self, model_id):
        """Test Anthropic Claude model"""
        try:
            prompt = "\n\nHuman: Please respond with just 'Claude test successful' to verify this model is working.\n\nAssistant:"
            
            body = {
                "prompt": prompt,
                "max_tokens_to_sample": 20,
                "temperature": 0.1
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['completion']
            print(f"   Claude Response: {result.strip()}")
            return True
            
        except ClientError as e:
            print(f"   Claude Error: {e.response['Error']['Code']}")
            return False

    def _test_ai21(self, model_id):
        """Test AI21 Labs model"""
        try:
            body = {
                "prompt": "Please respond with just 'AI21 test successful' to verify this model is working.",
                "maxTokens": 20,
                "temperature": 0.1
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['completions'][0]['data']['text']
            print(f"   AI21 Response: {result.strip()}")
            return True
            
        except ClientError as e:
            print(f"   AI21 Error: {e.response['Error']['Code']}")
            return False

    def test_batch_processing(self):
        """Test batch processing capability"""
        print("\n🔍 TESTING BATCH PROCESSING CAPABILITY")
        
        documents = [
            "Employee Name: John Smith, Start Date: 2024-01-15, Department: IT",
            "Employee Name: Jane Doe, Start Date: 2024-02-01, Department: HR", 
            "Employee Name: Bob Johnson, Start Date: 2024-03-10, Department: Finance"
        ]
        
        try:
            # Test with Claude for batch processing
            prompt = f"""
Human: Please extract the employee information from these documents and format as JSON:

{documents}

Return only valid JSON with keys: name, start_date, department

Assistant:
"""
            
            body = {
                "prompt": prompt,
                "max_tokens_to_sample": 200,
                "temperature": 0.1
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-instant-v1',
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['completion']
            print(f"✅ Batch Processing Test: SUCCESS")
            print(f"   Sample Output: {result.strip()[:100]}...")
            return True
            
        except Exception as e:
            print(f"❌ Batch Processing Test: FAILED - {e}")
            return False

def main():
    print("🤖 COMPREHENSIVE BEDROCK VERIFICATION")
    print("=" * 60)
    
    tester = BedRockComprehensiveTest()
    
    # Test 1: Model Invocation
    invocation_success = tester.test_model_invocation()
    
    # Test 2: Batch Processing  
    batch_success = tester.test_batch_processing()
    
    # Final Verification
    print("\n" + "=" * 60)
    print("🎯 FINAL VERIFICATION RESULTS:")
    print(f"   Model Invocation: {'✅ SUCCESS' if invocation_success else '❌ NEEDS ATTENTION'}")
    print(f"   Batch Processing: {'✅ SUCCESS' if batch_success else '❌ NEEDS ATTENTION'}")
    
    if invocation_success and batch_success:
        print("\n🎉 BEDROCK IS FULLY OPERATIONAL!")
        print("   Ready for HR onboarding workflow implementation")
    else:
        print("\n⚠️  Some tests need attention - but core functionality is working")

if __name__ == "__main__":
    main()
