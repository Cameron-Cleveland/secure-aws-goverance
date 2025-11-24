#!/usr/bin/env python3
"""
ROBUST HR Onboarding - Fixed BedRock Response Handling
"""

import boto3
import json
import re
import uuid
from datetime import datetime, timezone
from botocore.exceptions import ClientError

class RobustHROnboarding:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.comprehend = boto3.client('comprehend')
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Use the REAL S3 bucket from our Terraform deployment
        self.bucket_name = "secure-governance-demo-hr-documents-24b4c4beb8bde70f"
        
        print("🏢 ROBUST HR ONBOARDING WORKFLOW")
        print("=" * 60)
        print("Technologies: S3 + Comprehend + BedRock + IAM")
        print(f"S3 Bucket: {self.bucket_name}")
        print("=" * 60)
    
    def process_onboarding(self, employee_data):
        """Complete onboarding workflow with robust error handling"""
        print("🚀 STARTING ONBOARDING WORKFLOW")
        
        try:
            # Step 1: Store HR document in S3
            document_key = self._store_hr_document(employee_data)
            
            # Step 2: PII Compliance Check with Comprehend
            pii_findings = self._pii_compliance_check(employee_data)
            
            # Step 3: AI-Powered Data Extraction with better error handling
            user_data = self._extract_user_data_robust(employee_data)
            
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
                "upload_time": datetime.now(timezone.utc).isoformat(),
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
    
    def _extract_user_data_robust(self, employee_data):
        """Robust user data extraction with fallbacks"""
        print("🤖 Extracting user data with AI...")
        
        # Try BedRock first
        ai_extraction = self._try_bedrock_extraction_robust(employee_data)
        if ai_extraction and self._validate_user_data(ai_extraction):
            return ai_extraction
        
        # Fallback to rule-based extraction
        print("🔧 Using rule-based extraction")
        return self._rule_based_extraction(employee_data)
    
    def _try_bedrock_extraction_robust(self, employee_data):
        """Robust BedRock extraction with better error handling"""
        try:
            # More specific prompt for better results
            prompt = f"""
Human: Extract the following information from this HR data and return as VALID JSON with these exact keys: username, email, role, start_date, department, employee_id, manager.

IMPORTANT: 
- username should be first.last format from the name
- email should be the email address
- role should be the job position
- start_date should be YYYY-MM-DD format
- department should be the department name
- employee_id should be the employee ID
- manager should be the manager's name

HR Data: {json.dumps(employee_data)}

Return ONLY valid JSON with exactly those keys, no other text.

Example valid response:
{{
  "username": "john.doe",
  "email": "john.doe@company.com",
  "role": "Software Engineer", 
  "start_date": "2024-01-15",
  "department": "Engineering",
  "employee_id": "ENG-2024-001",
  "manager": "Jane Smith"
}}

Assistant:
"""
            
            body = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 500,
                    "temperature": 0.1
                }
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId='amazon.titan-text-express-v1',
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            result_text = response_body['results'][0]['outputText'].strip()
            
            print(f"   BedRock raw response: {result_text}")
            
            # Extract JSON with better pattern matching
            json_match = re.search(r'\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Clean up the JSON string
                json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                
                try:
                    user_data = json.loads(json_str)
                    print("   ✅ Successfully parsed BedRock JSON response")
                    return user_data
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON parsing failed: {e}")
                    print(f"   JSON string: {json_str}")
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ BedRock extraction failed: {e}")
            return None
    
    def _validate_user_data(self, user_data):
        """Validate that user data has all required fields"""
        required_fields = ['username', 'email', 'role', 'start_date', 'department', 'employee_id', 'manager']
        
        if not isinstance(user_data, dict):
            print("   ❌ User data is not a dictionary")
            return False
        
        missing_fields = [field for field in required_fields if field not in user_data]
        
        if missing_fields:
            print(f"   ❌ Missing required fields: {missing_fields}")
            print(f"   Available fields: {list(user_data.keys())}")
            return False
        
        # Validate field contents
        for field, value in user_data.items():
            if not value or str(value).strip() == '':
                print(f"   ❌ Empty value for field: {field}")
                return False
        
        print("   ✅ All required fields present and valid")
        return True
    
    def _rule_based_extraction(self, employee_data):
        """Rule-based extraction as fallback"""
        print("   🔧 Using rule-based fallback extraction")
        
        # Extract username from email or name
        email = employee_data.get('email', '')
        if email and '@' in email:
            username = email.split('@')[0]
        else:
            # Extract from name
            full_name = employee_data.get('full_name', 'Unknown User')
            name_parts = full_name.lower().split()
            if len(name_parts) >= 2:
                username = f"{name_parts[0]}.{name_parts[-1]}"
            else:
                username = name_parts[0] if name_parts else "user"
        
        # Clean username
        username = re.sub(r'[^a-z0-9.]', '', username)
        
        return {
            "username": username,
            "email": employee_data.get('email', f"{username}@company.com"),
            "role": employee_data.get('position', 'Employee'),
            "start_date": employee_data.get('start_date', datetime.now().strftime('%Y-%m-%d')),
            "department": employee_data.get('department', 'General'),
            "employee_id": employee_data.get('employee_id', 'EMP-' + str(uuid.uuid4())[:6].upper()),
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
    print("🚀 ROBUST HR ONBOARDING DEMONSTRATION")
    print("With improved BedRock response handling")
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
    
    onboarding = RobustHROnboarding()
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
