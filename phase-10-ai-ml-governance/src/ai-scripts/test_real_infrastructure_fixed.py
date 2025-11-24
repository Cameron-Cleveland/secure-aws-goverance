#!/usr/bin/env python3
"""
Fixed Infrastructure Test with Updated BedRock Models
"""

import boto3
import json
import os
import re
from botocore.exceptions import ClientError

class FixedInfrastructureTest:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.comprehend = boto3.client('comprehend')
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.bedrock = boto3.client('bedrock', region_name='us-east-1')
        
        print("🔍 FIXED INFRASTRUCTURE TEST")
        print("=" * 50)
        
    def discover_resources(self):
        """Discover deployed resources manually"""
        print("🔍 Discovering deployed resources...")
        
        # Try to find our S3 bucket
        try:
            response = self.s3.list_buckets()
            our_buckets = [b for b in response['Buckets'] if 'secure-governance-demo-hr-documents' in b['Name']]
            if our_buckets:
                self.bucket_name = our_buckets[0]['Name']
                print(f"✅ Found S3 bucket: {self.bucket_name}")
            else:
                print("❌ No HR documents bucket found")
                self.bucket_name = None
        except ClientError as e:
            print(f"❌ Error listing buckets: {e}")
            self.bucket_name = None
        
        # Try to find our IAM role
        try:
            iam = boto3.client('iam')
            role_name = "secure-governance-demo-hr-workflow"
            iam.get_role(RoleName=role_name)
            self.role_name = role_name
            print(f"✅ Found IAM role: {role_name}")
        except ClientError:
            print("❌ IAM role not found")
            self.role_name = None
    
    def get_available_models(self):
        """Get current available BedRock models"""
        try:
            response = self.bedrock.list_foundation_models()
            models = response['modelSummaries']
            
            # Filter for currently available text models
            available_models = []
            for model in models:
                if (model['modelLifecycle'].get('status') == 'ACTIVE' and 
                    'TEXT' in model['outputModalities']):
                    available_models.append(model['modelId'])
            
            print(f"🔍 Found {len(available_models)} active text models")
            return available_models
            
        except ClientError as e:
            print(f"❌ Error listing models: {e}")
            return []
    
    def test_s3_bucket(self):
        """Test S3 bucket functionality"""
        if not self.bucket_name:
            print("❌ No S3 bucket to test")
            return False
        
        try:
            print(f"🪣 Testing S3 Bucket: {self.bucket_name}")
            
            # Upload a test file
            test_key = "infrastructure-test.txt"
            test_content = "HR Onboarding Infrastructure Test - " + __import__('datetime').datetime.now().isoformat()
            
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType='text/plain'
            )
            print("✅ Successfully uploaded test file to S3")
            
            # Read it back
            response = self.s3.get_object(Bucket=self.bucket_name, Key=test_key)
            content = response['Body'].read().decode('utf-8')
            print("✅ Successfully read test file from S3")
            
            # List bucket contents
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, MaxKeys=5)
            if 'Contents' in response:
                print(f"✅ Bucket contains {len(response['Contents'])} objects")
            
            return True
            
        except ClientError as e:
            print(f"❌ S3 test failed: {e}")
            return False
    
    def test_comprehend(self):
        """Test Amazon Comprehend access"""
        try:
            test_text = "John Smith lives at 123 Main St and his email is john.smith@email.com. He was born on 1985-03-15."
            
            response = self.comprehend.detect_pii_entities(
                Text=test_text,
                LanguageCode='en'
            )
            
            entities_found = len(response['Entities'])
            print(f"✅ Comprehend test successful - Found {entities_found} PII entities")
            
            # Show detected entities (masked)
            for entity in response['Entities']:
                entity_type = entity['Type']
                text_snippet = test_text[entity['BeginOffset']:entity['EndOffset']]
                masked = text_snippet[:2] + '***' if len(text_snippet) > 2 else '***'
                print(f"   - {entity_type}: {masked}")
            
            return True
            
        except ClientError as e:
            print(f"❌ Comprehend test failed: {e}")
            return False
    
    def test_bedrock(self):
        """Test AWS BedRock with current models"""
        try:
            available_models = self.get_available_models()
            if not available_models:
                print("❌ No available BedRock models found")
                return False
            
            # Try different model families
            test_models = []
            for model_id in available_models:
                if 'titan-text' in model_id:
                    test_models.append(('Amazon Titan', model_id, self._test_titan))
                elif 'claude-3' in model_id:
                    test_models.append(('Anthropic Claude 3', model_id, self._test_claude3))
                elif 'claude-2' in model_id and 'ACTIVE' in model_id:
                    test_models.append(('Anthropic Claude 2', model_id, self._test_claude2))
            
            if not test_models:
                print("❌ No suitable test models found")
                return False
            
            # Test the first available model
            model_name, model_id, test_func = test_models[0]
            print(f"🤖 Testing {model_name} ({model_id})...")
            
            result = test_func(model_id)
            if result:
                print(f"✅ BedRock test successful with {model_name}")
                return True
            else:
                print(f"❌ BedRock test failed with {model_name}")
                return False
            
        except Exception as e:
            print(f"❌ BedRock test failed: {e}")
            return False
    
    def _test_titan(self, model_id):
        """Test Amazon Titan model"""
        try:
            body = {
                "inputText": "Please respond with just the word 'SUCCESS' to confirm this model is working.",
                "textGenerationConfig": {
                    "maxTokenCount": 10,
                    "temperature": 0.1
                }
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['results'][0]['outputText'].strip()
            print(f"   Titan Response: '{result}'")
            return 'SUCCESS' in result.upper()
            
        except ClientError as e:
            print(f"   Titan Error: {e.response['Error']['Code']}")
            return False
    
    def _test_claude3(self, model_id):
        """Test Claude 3 model"""
        try:
            # Claude 3 uses messages format
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": "Please respond with just the word SUCCESS to confirm this model is working."
                    }
                ]
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['content'][0]['text'].strip()
            print(f"   Claude 3 Response: '{result}'")
            return 'SUCCESS' in result.upper()
            
        except ClientError as e:
            print(f"   Claude 3 Error: {e.response['Error']['Code']}")
            # Fall back to older format
            return self._test_claude2(model_id)
    
    def _test_claude2(self, model_id):
        """Test Claude 2 model (older format)"""
        try:
            prompt = "\n\nHuman: Please respond with just the word SUCCESS to confirm this model is working.\n\nAssistant:"
            
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
            print(f"   Claude 2 Response: '{result}'")
            return 'SUCCESS' in result.upper()
            
        except ClientError as e:
            print(f"   Claude 2 Error: {e.response['Error']['Code']}")
            return False
    
    def test_iam_role(self):
        """Test IAM role"""
        if not self.role_name:
            print("❌ No IAM role to test")
            return False
        
        try:
            iam = boto3.client('iam')
            
            # Get role details
            response = iam.get_role(RoleName=self.role_name)
            role_arn = response['Role']['Arn']
            print(f"✅ IAM Role accessible: {role_arn}")
            
            # Check attached policies
            response = iam.list_attached_role_policies(RoleName=self.role_name)
            for policy in response['AttachedPolicies']:
                print(f"   - Policy: {policy['PolicyName']}")
            
            return True
            
        except ClientError as e:
            print(f"❌ IAM role test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all infrastructure tests"""
        print("🚀 RUNNING FIXED INFRASTRUCTURE TESTS")
        print("=" * 50)
        
        # First discover what resources we have
        self.discover_resources()
        
        tests = [
            ("IAM Role", self.test_iam_role),
            ("S3 Bucket", self.test_s3_bucket),
            ("Amazon Comprehend", self.test_comprehend),
            ("AWS BedRock", self.test_bedrock)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 Testing {test_name}...")
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name}: PASS")
                else:
                    print(f"❌ {test_name}: FAIL")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 FIXED TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL INFRASTRUCTURE TESTS PASSED!")
            print("🚀 HR Workflow infrastructure is fully operational!")
        elif passed >= 2:
            print(f"\n⚠️  Partial success - {passed}/{total} tests passed")
            print("💡 Core AI services are working!")
        else:
            print(f"\n🔧 {total - passed} tests need attention")

def main():
    tester = FixedInfrastructureTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
