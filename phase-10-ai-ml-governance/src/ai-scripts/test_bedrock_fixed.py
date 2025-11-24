#!/usr/bin/env python3
"""
Fixed BedRock Test with Available Models
"""

import boto3
import json
from botocore.exceptions import ClientError

class BedRockTester:
    def __init__(self):
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.bedrock = boto3.client('bedrock', region_name='us-east-1')
        
    def get_available_models(self):
        """Get models that are actually available for invocation"""
        try:
            response = self.bedrock.list_foundation_models()
            available_models = []
            
            for model in response['modelSummaries']:
                # Check if model is active and supports text
                if (model['modelLifecycle'].get('status') == 'ACTIVE' and 
                    'TEXT' in model['outputModalities']):
                    
                    # Try to get model details to check availability
                    try:
                        model_detail = self.bedrock.get_foundation_model(
                            modelIdentifier=model['modelId']
                        )
                        # If we can get details, it's likely available
                        available_models.append({
                            'modelId': model['modelId'],
                            'modelName': model['modelName'],
                            'provider': model['providerName']
                        })
                    except ClientError:
                        continue  # Skip models we can't access
            
            return available_models
            
        except ClientError as e:
            print(f"❌ Error listing models: {e}")
            return []
    
    def test_model_invocation(self, model_id):
        """Test if we can actually invoke a model"""
        print(f"🤖 Testing {model_id}...")
        
        # Try different invocation formats based on provider
        if 'titan' in model_id.lower():
            return self._test_titan(model_id)
        elif 'claude-3' in model_id.lower():
            return self._test_claude3(model_id)
        elif 'claude-2' in model_id.lower():
            return self._test_claude2(model_id)
        elif 'claude-instant' in model_id.lower():
            return self._test_claude_instant(model_id)
        elif 'j2' in model_id.lower():
            return self._test_ai21(model_id)
        else:
            return self._test_generic(model_id)
    
    def _test_titan(self, model_id):
        """Test Amazon Titan models"""
        try:
            body = {
                "inputText": "Hello, please respond with just the word SUCCESS.",
                "textGenerationConfig": {
                    "maxTokenCount": 10,
                    "temperature": 0.1
                }
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['results'][0]['outputText'].strip()
            print(f"   ✅ Titan Response: '{result}'")
            return True
            
        except ClientError as e:
            print(f"   ❌ Titan Error: {e.response['Error']['Code']}")
            return False
    
    def _test_claude3(self, model_id):
        """Test Claude 3 models with new message format"""
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": "Please respond with just the word SUCCESS."
                    }
                ]
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['content'][0]['text'].strip()
            print(f"   ✅ Claude 3 Response: '{result}'")
            return True
            
        except ClientError as e:
            print(f"   ❌ Claude 3 Error: {e.response['Error']['Code']}")
            return False
    
    def _test_claude2(self, model_id):
        """Test Claude 2 models"""
        try:
            prompt = "\n\nHuman: Please respond with just the word SUCCESS.\n\nAssistant:"
            
            body = {
                "prompt": prompt,
                "max_tokens_to_sample": 10,
                "temperature": 0.1
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['completion'].strip()
            print(f"   ✅ Claude 2 Response: '{result}'")
            return True
            
        except ClientError as e:
            print(f"   ❌ Claude 2 Error: {e.response['Error']['Code']}")
            return False
    
    def _test_claude_instant(self, model_id):
        """Test Claude Instant models"""
        try:
            prompt = "\n\nHuman: Please respond with just the word SUCCESS.\n\nAssistant:"
            
            body = {
                "prompt": prompt,
                "max_tokens_to_sample": 10,
                "temperature": 0.1
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['completion'].strip()
            print(f"   ✅ Claude Instant Response: '{result}'")
            return True
            
        except ClientError as e:
            print(f"   ❌ Claude Instant Error: {e.response['Error']['Code']}")
            return False
    
    def _test_ai21(self, model_id):
        """Test AI21 Labs models"""
        try:
            body = {
                "prompt": "Please respond with just the word SUCCESS.",
                "maxTokens": 10,
                "temperature": 0.1
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['completions'][0]['data']['text'].strip()
            print(f"   ✅ AI21 Response: '{result}'")
            return True
            
        except ClientError as e:
            print(f"   ❌ AI21 Error: {e.response['Error']['Code']}")
            return False
    
    def _test_generic(self, model_id):
        """Generic test for other models"""
        try:
            # Try a simple prompt
            body = {
                "prompt": "Say SUCCESS",
                "maxTokens": 10
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            # If we get here, the invocation worked
            print(f"   ✅ {model_id} - Invocation successful")
            return True
            
        except ClientError as e:
            print(f"   ❌ {model_id} - Error: {e.response['Error']['Code']}")
            return False
    
    def run_comprehensive_test(self):
        """Test all available models"""
        print("🚀 COMPREHENSIVE BEDROCK TEST")
        print("=" * 50)
        
        # Get available models
        available_models = self.get_available_models()
        print(f"🔍 Found {len(available_models)} potentially available models")
        
        if not available_models:
            print("❌ No models available for testing")
            return False
        
        # Test each model
        successful_models = []
        failed_models = []
        
        for model in available_models[:10]:  # Test first 10 to avoid rate limits
            model_id = model['modelId']
            print(f"\n🎯 Testing {model['provider']} - {model['modelName']}")
            
            if self.test_model_invocation(model_id):
                successful_models.append(model)
            else:
                failed_models.append(model)
            
            # Small delay to avoid throttling
            import time
            time.sleep(1)
        
        # Results
        print("\n" + "=" * 50)
        print("📊 BEDROCK TEST RESULTS")
        print("=" * 50)
        print(f"✅ Successful: {len(successful_models)} models")
        print(f"❌ Failed: {len(failed_models)} models")
        
        if successful_models:
            print("\n🎉 WORKING MODELS:")
            for model in successful_models:
                print(f"   ✅ {model['modelId']}")
            
            print(f"\n🚀 BedRock is WORKING with {len(successful_models)} models!")
            return True
        else:
            print("\n🔧 No models could be invoked. Possible issues:")
            print("   - Model access not enabled in console")
            print("   - Region restrictions")
            print("   - IAM permissions need updating")
            return False

def main():
    tester = BedRockTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 BEDROCK IS OPERATIONAL!")
        print("💡 Your HR onboarding workflow will work with BedRock!")
    else:
        print("\n⚠️  BedRock needs configuration")
        print("💡 Check AWS Console → BedRock → Model Access")

if __name__ == "__main__":
    main()
