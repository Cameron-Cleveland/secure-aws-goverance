#!/usr/bin/env python3
"""
Test REAL Terraform-deployed HR Workflow Infrastructure
"""

import boto3
import json
import subprocess
import re
from botocore.exceptions import ClientError

def get_terraform_outputs():
    """Get Terraform outputs to find our deployed resources"""
    try:
        result = subprocess.run(
            ['terraform', 'output', '-json'], 
            cwd='../../terraform',
            capture_output=True, 
            text=True,
            check=True
        )
        outputs = json.loads(result.stdout)
        return outputs
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running terraform output: {e}")
        return {}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

class RealInfrastructureTest:
    def __init__(self):
        self.outputs = get_terraform_outputs()
        self.s3 = boto3.client('s3')
        self.comprehend = boto3.client('comprehend')
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        print("🔍 REAL INFRASTRUCTURE TEST")
        print("=" * 50)
        
    def test_s3_bucket(self):
        """Test the S3 bucket created by Terraform"""
        bucket_name = self.outputs.get('hr_documents_bucket', {}).get('value', '')
        if not bucket_name:
            print("❌ No S3 bucket found in Terraform outputs")
            return False
        
        try:
            print(f"🪣 Testing S3 Bucket: {bucket_name}")
            
            # Check if bucket exists and we can access it
            self.s3.head_bucket(Bucket=bucket_name)
            print("✅ S3 bucket exists and is accessible")
            
            # Upload a test file
            test_key = "test-infrastructure.txt"
            test_content = "This is a test file for HR onboarding infrastructure"
            
            self.s3.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType='text/plain'
            )
            print("✅ Successfully uploaded test file to S3")
            
            # Read it back
            response = self.s3.get_object(Bucket=bucket_name, Key=test_key)
            content = response['Body'].read().decode('utf-8')
            print("✅ Successfully read test file from S3")
            
            return True
            
        except ClientError as e:
            print(f"❌ S3 test failed: {e}")
            return False
    
    def test_comprehend(self):
        """Test Amazon Comprehend access"""
        try:
            test_text = "John Smith lives at 123 Main St and his email is john.smith@email.com"
            
            response = self.comprehend.detect_pii_entities(
                Text=test_text,
                LanguageCode='en'
            )
            
            entities_found = len(response['Entities'])
            print(f"✅ Comprehend test successful - Found {entities_found} PII entities")
            
            for entity in response['Entities']:
                entity_type = entity['Type']
                text_snippet = test_text[entity['BeginOffset']:entity['EndOffset']]
                print(f"   - {entity_type}: {text_snippet[:3]}***")
            
            return True
            
        except ClientError as e:
            print(f"❌ Comprehend test failed: {e}")
            return False
    
    def test_bedrock(self):
        """Test AWS BedRock access"""
        try:
            prompt = "\n\nHuman: Please respond with just 'BedRock test successful' to confirm access.\n\nAssistant:"
            
            body = {
                "prompt": prompt,
                "max_tokens_to_sample": 20,
                "temperature": 0.1
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-instant-v1',
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['completion'].strip()
            print(f"✅ BedRock test successful - Response: {result}")
            
            return True
            
        except ClientError as e:
            print(f"❌ BedRock test failed: {e}")
            return False
    
    def test_iam_role(self):
        """Test that IAM role was created"""
        role_arn = self.outputs.get('hr_workflow_role_arn', {}).get('value', '')
        if not role_arn:
            print("❌ No IAM role found in Terraform outputs")
            return False
        
        print(f"👤 IAM Role created: {role_arn}")
        return True
    
    def run_all_tests(self):
        """Run all infrastructure tests"""
        tests = [
            ("IAM Role", self.test_iam_role),
            ("S3 Bucket", self.test_s3_bucket),
            ("Amazon Comprehend", self.test_comprehend),
            ("AWS BedRock", self.test_bedrock)
        ]
        
        print("\n🚀 RUNNING INFRASTRUCTURE TESTS")
        print("=" * 50)
        
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
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL INFRASTRUCTURE TESTS PASSED!")
            print("🚀 HR Workflow infrastructure is ready!")
        else:
            print(f"\n⚠️  {total - passed} tests need attention")

def main():
    tester = RealInfrastructureTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
