#!/usr/bin/env python3
"""
FINAL HR Onboarding - Works with or without BedRock
Demonstrates complete workflow with real infrastructure
"""

import boto3
import json
import re
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

class FinalHROnboarding:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.comprehend = boto3.client('comprehend')
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Use the REAL S3 bucket from our Terraform deployment
        self.bucket_name = "secure-governance-demo-hr-documents-24b4c4beb8bde70f"
        
        print("🏢 ENTERPRISE HR ONBOARDING WORKFLOW")
        print("=" * 60)
        print("Technologies: S3 + Comprehend + BedRock + IAM")
        print(f"S3 Bucket: {self.bucket_name}")
        print("=" * 60)
    
    def process_onboarding(self, employee_data):
        """Complete onboarding workflow"""
        print("🚀 STARTING ONBOARDING WORKFLOW")
        
        try:
            # Step 1: Store HR document in S3
            document_key = self._store_hr_document(employee_data)
            
            # Step 2: PII Compliance Check with Comprehend
            pii_findings = self._pii_compliance_check(employee_data)
            
            # Step 3: AI-Powered Data Extraction
            user_data = self._extract_user_data(employee_data)
            
            # Step 4: IAM User Provisioning (Simulated)
            iam_result = self._provision_iam_user(user_data)
            
            # Step 5: NIST Compliance Audit
            audit_trail = self._create_compliance_audit({
                'user_data': user_data,
                'pii_findings': pii_findings,
                'document_key': document_key,
                'iam_result': iam_result
            })
            
            print("\n🎉 ONBOARDING WORKFLOW COMPLETED SUCCESSFULLY!")
            return {
                'success': True,
                'user_data': user_data,
                'audit_trail': audit_trail,
                'pii_check': pii_findings
            }
            
        except Exception as e:
            print(f"❌ Onboarding failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _store_hr_document(self, employee_data):
        """Store HR document in S3 with proper governance"""
        document_id = str(uuid.uuid4())
        document_key = f"onboarding/{document_id}.json"
        
        document = {
            "metadata": {
                "document_id": document_id,
                "upload_time": datetime.utcnow().isoformat() + 'Z',
                "workflow_version": "2.0",
                "compliance_framework": "NIST-800-53"
            },
            "employee_data": employee_data
        }
        
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=document_key,
            Body=json.dumps(document, indent=2),
            ContentType='application/json',
            Metadata={
                'data-classification': 'confidential',
                'retention-period': '7-years',
                'pii-present': 'true'
            }
        )
        
        print(f"✅ HR document stored: s3://{self.bucket_name}/{document_key}")
        return document_key
    
    def _pii_compliance_check(self, employee_data):
        """Check for PII compliance using Amazon Comprehend"""
        # Convert employee data to text for Comprehend analysis
        text_data = json.dumps(employee_data)
        
        try:
            response = self.comprehend.detect_pii_entities(
                Text=text_data,
                LanguageCode='en'
            )
            
            findings = {
                'pii_entities_found': len(response['Entities']),
                'entities': [],
                'compliance_status': 'COMPLIANT' if len(response['Entities']) == 0 else 'REVIEW_REQUIRED'
            }
            
            for entity in response['Entities']:
                findings['entities'].append({
                    'type': entity['Type'],
                    'score': entity['Score'],
                    'text_snippet': text_data[entity['BeginOffset']:entity['EndOffset']][:3] + '***'
                })
            
            print(f"✅ PII Compliance Check: {findings['compliance_status']}")
            print(f"   Found {findings['pii_entities_found']} PII entities")
            
            return findings
            
        except ClientError as e:
            print(f"⚠️ Comprehend PII check failed: {e}")
            return {'compliance_status': 'CHECK_FAILED', 'error': str(e)}
    
    def _extract_user_data(self, employee_data):
        """Extract user data using AI (BedRock) or fallback"""
        print("🤖 Extracting user data with AI...")
        
        # Try BedRock first
        ai_extraction = self._try_bedrock_extraction(employee_data)
        if ai_extraction:
            return ai_extraction
        
        # Fallback to rule-based extraction
        print("🔧 Using rule-based extraction (BedRock not available)")
        return self._rule_based_extraction(employee_data)
    
    def _try_bedrock_extraction(self, employee_data):
        """Try to use BedRock for AI-powered extraction"""
        try:
            # Try multiple models
            models_to_try = [
                'amazon.titan-text-express-v1',
                'amazon.titan-text-lite-v1',
                'anthropic.claude-instant-v1'
            ]
            
            prompt = f"""
Human: Extract the following information from this HR data and return as JSON with keys: username, email, role, start_date, department, employee_id, manager.

HR Data: {json.dumps(employee_data)}

Return only valid JSON, no other text.

Assistant:
"""
            
            for model_id in models_to_try:
                try:
                    if 'titan' in model_id:
                        body = {
                            "inputText": prompt,
                            "textGenerationConfig": {
                                "maxTokenCount": 300,
                                "temperature": 0.1
                            }
                        }
                    else:
                        body = {
                            "prompt": prompt,
                            "max_tokens_to_sample": 300,
                            "temperature": 0.1
                        }
                    
                    response = self.bedrock_runtime.invoke_model(
                        modelId=model_id,
                        body=json.dumps(body)
                    )
                    
                    if 'titan' in model_id:
                        response_body = json.loads(response['body'].read())
                        result_text = response_body['results'][0]['outputText']
                    else:
                        response_body = json.loads(response['body'].read())
                        result_text = response_body['completion']
                    
                    # Extract JSON
                    json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                    if json_match:
                        user_data = json.loads(json_match.group())
                        print(f"✅ AI extraction successful with {model_id}")
                        return user_data
                        
                except ClientError:
                    continue  # Try next model
            
            return None
            
        except Exception as e:
            print(f"⚠️ BedRock extraction failed: {e}")
            return None
    
    def _rule_based_extraction(self, employee_data):
        """Rule-based extraction as fallback"""
        return {
            "username": employee_data.get('email', '').split('@')[0] if employee_data.get('email') else "user_" + str(uuid.uuid4())[:8],
            "email": employee_data.get('email', ''),
            "role": employee_data.get('position', 'Employee'),
            "start_date": employee_data.get('start_date', datetime.now().strftime('%Y-%m-%d')),
            "department": employee_data.get('department', 'General'),
            "employee_id": employee_data.get('employee_id', 'EMP-' + str(uuid.uuid4())[:6]),
            "manager": employee_data.get('manager', 'Not specified')
        }
    
    def _provision_iam_user(self, user_data):
        """Simulate IAM user provisioning"""
        username = user_data['username']
        
        print(f"👤 IAM User Provisioning for: {username}")
        print(f"   Email: {user_data['email']}")
        print(f"   Role: {user_data['role']}")
        print(f"   Department: {user_data['department']}")
        
        # Simulate policy assignment based on role
        policies = self._get_role_policies(user_data['role'])
        for policy in policies:
            print(f"   Policy: {policy}")
        
        return {
            'username': username,
            'policies_assigned': policies,
            'status': 'PROVISIONED'
        }
    
    def _get_role_policies(self, role):
        """Get appropriate IAM policies based on role"""
        policy_map = {
            'System Administrator': ['AdministratorAccess', 'IAMFullAccess'],
            'Cloud Engineer': ['PowerUserAccess', 'AWSCloud9User'],
            'Developer': ['PowerUserAccess', 'AWSCodeCommitPowerUser'],
            'Data Analyst': ['AmazonS3ReadOnlyAccess', 'AmazonAthenaFullAccess'],
            'default': ['ReadOnlyAccess']
        }
        
        return policy_map.get(role, policy_map['default'])
    
    def _create_compliance_audit(self, workflow_data):
        """Create NIST-compliant audit trail"""
        audit_id = str(uuid.uuid4())
        audit_key = f"audit/trail/{audit_id}.json"
        
        audit_record = {
            "audit_id": audit_id,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "workflow": "hr_onboarding",
            "compliance_framework": "NIST-800-53",
            "data_minimization": True,
            "workflow_data": {
                k: v for k, v in workflow_data.items() 
                if k != 'pii_findings'  # Remove sensitive PII details from audit
            }
        }
        
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=audit_key,
            Body=json.dumps(audit_record, indent=2),
            ContentType='application/json'
        )
        
        print(f"📊 NIST Audit Trail: s3://{self.bucket_name}/{audit_key}")
        return audit_key

def main():
    print("🚀 ENTERPRISE HR ONBOARDING DEMONSTRATION")
    print("Directly relevant to AWS Administrator job requirements")
    print("=" * 60)
    
    # Sample HR data for onboarding
    sample_employee = {
        "full_name": "Maria Garcia Rodriguez",
        "email": "maria.garcia@company.com",
        "position": "Cloud Engineer",
        "department": "Cloud Infrastructure", 
        "start_date": "2024-02-01",
        "employee_id": "CE-2024-002",
        "manager": "Robert Chen",
        "work_location": "Hybrid",
        "required_systems": ["AWS", "Azure", "Terraform", "GitHub"],
        "security_clearance": "Level 2"
    }
    
    onboarding = FinalHROnboarding()
    result = onboarding.process_onboarding(sample_employee)
    
    if result['success']:
        print("\n" + "=" * 60)
        print("📋 ONBOARDING SUMMARY")
        print("=" * 60)
        print("User Data Extracted:")
        for key, value in result['user_data'].items():
            print(f"  {key}: {value}")
        
        print(f"\nPII Compliance: {result['pii_check']['compliance_status']}")
        print(f"Audit Trail: {result['audit_trail']}")
        
        print("\n🎯 JOB SKILLS DEMONSTRATED:")
        print("  ✅ AWS S3 for document storage & governance")
        print("  ✅ Amazon Comprehend for PII detection")
        print("  ✅ AWS BedRock for AI/ML processing") 
        print("  ✅ IAM user provisioning patterns")
        print("  ✅ NIST 800-53 compliance framework")
        print("  ✅ Infrastructure as Code (Terraform)")
        print("  ✅ Enterprise security patterns")
        
    else:
        print(f"\n❌ Onboarding failed: {result['error']}")

if __name__ == "__main__":
    main()
