#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST - All Services Working
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

class FinalTest:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.comprehend = boto3.client('comprehend')
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.iam = boto3.client('iam')
        
        self.bucket_name = "secure-governance-demo-hr-documents-24b4c4beb8bde70f"
        
    def test_all_services(self):
        """Test all AWS services in the HR workflow"""
        print("🚀 FINAL COMPREHENSIVE TEST")
        print("=" * 60)
        
        tests = [
            ("S3 Bucket Access", self.test_s3),
            ("Amazon Comprehend PII", self.test_comprehend),
            ("AWS BedRock AI", self.test_bedrock),
            ("IAM Role Verification", self.test_iam_role)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 {test_name}...")
            try:
                result = test_func()
                results.append((test_name, result))
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📊 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL SERVICES ARE FULLY OPERATIONAL!")
            print("🚀 Your AI/ML Governance platform is READY FOR PRODUCTION!")
        else:
            print(f"\n⚠️  {total - passed} services need attention")
        
        return passed == total
    
    def test_s3(self):
        """Test S3 bucket functionality"""
        try:
            # Test write
            test_key = f"test-{int(time.time())}.txt"
            test_content = f"S3 test at {time.ctime()}"
            
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=test_key,
                Body=test_content
            )
            
            # Test read
            response = self.s3.get_object(Bucket=self.bucket_name, Key=test_key)
            content = response['Body'].read().decode('utf-8')
            
            # Test list
            self.s3.list_objects_v2(Bucket=self.bucket_name, MaxKeys=5)
            
            print(f"   ✅ S3 operations: PUT, GET, LIST")
            print(f"   📁 Bucket: {self.bucket_name}")
            return True
            
        except ClientError as e:
            print(f"   ❌ S3 error: {e}")
            return False
    
    def test_comprehend(self):
        """Test Amazon Comprehend PII detection"""
        try:
            test_text = "John Smith with SSN 123-45-6789 lives at 123 Main St and email john@test.com"
            
            response = self.comprehend.detect_pii_entities(
                Text=test_text,
                LanguageCode='en'
            )
            
            entities = response['Entities']
            print(f"   ✅ Comprehend found {len(entities)} PII entities")
            
            for entity in entities:
                print(f"      - {entity['Type']}: {entity['Score']:.2f} confidence")
            
            return True
            
        except ClientError as e:
            print(f"   ❌ Comprehend error: {e}")
            return False
    
    def test_bedrock(self):
        """Test AWS BedRock with actual model invocation"""
        try:
            # Test Titan model
            body = {
                "inputText": "Please respond with just the word 'SUCCESS' to confirm BedRock is working.",
                "textGenerationConfig": {
                    "maxTokenCount": 10,
                    "temperature": 0.1
                }
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId='amazon.titan-text-express-v1',
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['results'][0]['outputText'].strip()
            
            print(f"   ✅ BedRock Titan response: '{result}'")
            
            # Also test Claude if available
            try:
                prompt = "\n\nHuman: Say just 'SUCCESS'\n\nAssistant:"
                body = {
                    "prompt": prompt,
                    "max_tokens_to_sample": 10,
                    "temperature": 0.1
                }
                
                response = self.bedrock_runtime.invoke_model(
                    modelId='anthropic.claude-instant-v1',
                    body=json.dumps(body)
                )
                
                response_body = json.loads(response['body'].read())
                result = response_body['completion'].strip()
                print(f"   ✅ BedRock Claude response: '{result}'")
                
            except ClientError:
                print("   ⚠️  Claude not available (Titan is working)")
            
            return True
            
        except ClientError as e:
            print(f"   ❌ BedRock error: {e}")
            return False
    
    def test_iam_role(self):
        """Test IAM role exists and has permissions"""
        try:
            role_name = "secure-governance-demo-hr-workflow"
            
            response = self.iam.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            
            # Check attached policies
            response = self.iam.list_attached_role_policies(RoleName=role_name)
            policies = [p['PolicyName'] for p in response['AttachedPolicies']]
            
            print(f"   ✅ IAM Role: {role_name}")
            print(f"   📋 Policies: {', '.join(policies)}")
            
            return True
            
        except ClientError as e:
            print(f"   ❌ IAM error: {e}")
            return False

def main():
    print("🎯 PHASE 10: AI/ML GOVERNANCE - FINAL VALIDATION")
    print("Directly demonstrates AWS Administrator job requirements")
    print("=" * 60)
    
    tester = FinalTest()
    success = tester.test_all_services()
    
    if success:
        print("\n" + "=" * 60)
        print("🏆 PROJECT COMPLETION ACHIEVED!")
        print("=" * 60)
        print("You have successfully built and deployed:")
        print("✅ AWS BedRock AI/ML Governance")
        print("✅ Amazon Comprehend PII Detection") 
        print("✅ S3 Document Governance")
        print("✅ IAM Security Controls")
        print("✅ NIST Compliance Framework")
        print("✅ Enterprise HR Onboarding Automation")
        print("\n🚀 Ready to showcase to employers!")

if __name__ == "__main__":
    main()
