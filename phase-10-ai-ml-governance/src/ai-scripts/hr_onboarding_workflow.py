#!/usr/bin/env python3
"""
HR Onboarding Automation Workflow
Uses Amazon Comprehend + BedRock to process HR documents and create user accounts
NIST Compliant: Extracts minimal necessary data for audit/accountability
"""

import boto3
import json
import uuid
import re
from datetime import datetime
from botocore.exceptions import ClientError

class HROnboardingWorkflow:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.comprehend = boto3.client('comprehend')
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.iam = boto3.client('iam')
        
        # NIST Required Fields for Audit/Accountability
        self.required_fields = [
            'username', 'email', 'role', 'start_date', 
            'department', 'employee_id', 'manager'
        ]
    
    def process_hr_document(self, bucket_name, document_key):
        """Main workflow to process HR document"""
        print(f"🚀 PROCESSING HR DOCUMENT: {document_key}")
        print("=" * 60)
        
        try:
            # Step 1: Extract text from document (simulated)
            document_text = self._simulate_document_extraction(bucket_name, document_key)
            
            # Step 2: PII Extraction with Comprehend
            print("🔍 Step 1: Extracting PII with Amazon Comprehend...")
            pii_entities = self._extract_pii_with_comprehend(document_text)
            
            # Step 3: Data Validation & Enhancement with BedRock
            print("🤖 Step 2: Validating data with AWS BedRock...")
            validated_data = self._validate_with_bedrock(document_text, pii_entities)
            
            # Step 4: Create IAM User (or prepare for Entra ID)
            print("👤 Step 3: Creating user account...")
            user_created = self._create_iam_user(validated_data)
            
            # Step 5: Audit Logging
            print("📊 Step 4: Creating audit trail...")
            self._create_audit_log(validated_data, document_key)
            
            print(f"✅ ONBOARDING COMPLETE for {validated_data.get('username', 'Unknown')}")
            return validated_data
            
        except Exception as e:
            print(f"❌ Onboarding failed: {e}")
            return None
    
    def _simulate_document_extraction(self, bucket_name, document_key):
        """Simulate document text extraction (in real scenario, use Textract)"""
        # Simulated HR onboarding document
        hr_document = """
        EMPLOYEE ONBOARDING FORM
        
        Personal Information:
        - Full Name: John Alexander Smith
        - Date of Birth: 1985-03-15
        - Social Security Number: 123-45-6789
        - Driver's License: D12345678 (State: CA)
        
        Employment Details:
        - Position: System Administrator
        - Employee ID: SA-2024-001
        - Department: Information Technology
        - Start Date: 2024-01-15
        - Manager: Sarah Johnson
        - Work Location: Remote
        
        Contact Information:
        - Email: john.smith@company.com
        - Phone: +1-555-0123
        - Address: 123 Main St, San Francisco, CA 94105
        
        System Access Requirements:
        - Required Systems: Active Directory, Azure, AWS, VMware
        - Security Clearance: Level 2
        - Role: System Administrator
        """
        
        print("   📄 Simulated document extraction complete")
        return hr_document
    
    def _extract_pii_with_comprehend(self, text):
        """Extract PII using Amazon Comprehend"""
        try:
            # Detect PII entities
            response = self.comprehend.detect_pii_entities(
                Text=text,
                LanguageCode='en'
            )
            
            entities = response['Entities']
            print(f"   ✅ Comprehend found {len(entities)} PII entities")
            
            # Extract specific entity values using regex (simplified)
            extracted_data = {
                'name': self._extract_name(text),
                'email': self._extract_email(text),
                'phone': self._extract_phone(text),
                'ssn': self._extract_ssn(text),
                'employee_id': self._extract_employee_id(text),
                'start_date': self._extract_date(text)
            }
            
            # Print extracted PII (masked for security)
            for key, value in extracted_data.items():
                if value:
                    masked_value = value[:3] + '***' if len(value) > 5 else '***'
                    print(f"   📋 {key}: {masked_value}")
            
            return extracted_data
            
        except ClientError as e:
            print(f"   ❌ Comprehend error: {e}")
            return {}
    
    def _validate_with_bedrock(self, document_text, pii_entities):
        """Use BedRock to validate and enhance extracted data"""
        try:
            prompt = f"""
Human: You are an HR data validation system. Please extract and validate the following information from the HR document:

DOCUMENT:
{document_text}

EXTRACTED PII:
{json.dumps(pii_entities, indent=2)}

Please extract and return ONLY these NIST-required fields in JSON format:
- username (generate from name: first.last)
- email (must be valid email format)
- role (job title)
- start_date (YYYY-MM-DD format)
- department
- employee_id
- manager

Return ONLY valid JSON, no other text.

Assistant:
"""
            
            body = {
                "prompt": prompt,
                "max_tokens_to_sample": 500,
                "temperature": 0.1
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-instant-v1',
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            completion = response_body['completion'].strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', completion, re.DOTALL)
            if json_match:
                validated_data = json.loads(json_match.group())
                print("   ✅ BedRock validation successful")
                return validated_data
            else:
                print("   ❌ BedRock returned invalid JSON")
                return {}
                
        except Exception as e:
            print(f"   ❌ BedRock validation error: {e}")
            return {}
    
    def _create_iam_user(self, user_data):
        """Create IAM user based on validated data (or prepare for Entra ID)"""
        try:
            username = user_data.get('username', f"user_{uuid.uuid4().hex[:8]}")
            
            # In production, you would create actual IAM user
            # For demo, we'll just simulate and print
            print(f"   👤 IAM User Creation Simulation:")
            print(f"      Username: {username}")
            print(f"      Email: {user_data.get('email')}")
            print(f"      Role: {user_data.get('role')}")
            print(f"      Department: {user_data.get('department')}")
            
            # Simulate IAM policy assignment based on role
            policies = self._get_role_policies(user_data.get('role'))
            for policy in policies:
                print(f"      Policy: {policy}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ IAM creation error: {e}")
            return False
    
    def _get_role_policies(self, role):
        """Get appropriate IAM policies based on role"""
        role_policies = {
            'System Administrator': [
                'AdministratorAccess',
                'IAMFullAccess'
            ],
            'Developer': [
                'PowerUserAccess',
                'AWSCloud9User'
            ],
            'Data Analyst': [
                'AmazonS3ReadOnlyAccess',
                'AmazonAthenaFullAccess'
            ]
        }
        
        return role_policies.get(role, ['ReadOnlyAccess'])
    
    def _create_audit_log(self, user_data, document_key):
        """Create NIST-compliant audit trail"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'action': 'user_onboarding',
            'user_data': {k: v for k, v in user_data.items() if k != 'ssn'},  # Remove sensitive data
            'source_document': document_key,
            'workflow_version': '1.0',
            'compliance_framework': 'NIST-800-53'
        }
        
        print("   📊 Audit log created (NIST compliant)")
        print(f"      Framework: {audit_entry['compliance_framework']}")
        print(f"      Timestamp: {audit_entry['timestamp']}")
    
    # Helper methods for PII extraction
    def _extract_name(self, text):
        match = re.search(r'Name:\s*([A-Za-z\s]+)', text)
        return match.group(1).strip() if match else None
    
    def _extract_email(self, text):
        match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return match.group() if match else None
    
    def _extract_phone(self, text):
        match = re.search(r'[\+]?[1]?[-\.\s]?\(?[\d]{3}\)?[-\.\s]?[\d]{3}[-\.\s]?[\d]{4}', text)
        return match.group() if match else None
    
    def _extract_ssn(self, text):
        match = re.search(r'\d{3}-\d{2}-\d{4}', text)
        return match.group() if match else None
    
    def _extract_employee_id(self, text):
        match = re.search(r'Employee ID:\s*([A-Z0-9-]+)', text)
        return match.group(1) if match else None
    
    def _extract_date(self, text):
        match = re.search(r'Start Date:\s*(\d{4}-\d{2}-\d{2})', text)
        return match.group(1) if match else None

def main():
    print("🏢 HR ONBOARDING AUTOMATION WORKFLOW")
    print("=" * 60)
    print("NIST Compliant - Minimal Data Extraction for Audit")
    print("Technologies: Amazon Comprehend + AWS BedRock + IAM")
    print("=" * 60)
    
    workflow = HROnboardingWorkflow()
    
    # Process sample HR document
    bucket_name = "hr-documents-bucket"
    document_key = "onboarding/john-smith-2024.pdf"
    
    result = workflow.process_hr_document(bucket_name, document_key)
    
    if result:
        print("\n🎉 ONBOARDING WORKFLOW COMPLETED SUCCESSFULLY!")
        print("📋 Final User Data (NIST Minimal Set):")
        for field in workflow.required_fields:
            value = result.get(field, 'Not found')
            masked_value = value[:3] + '***' if field in ['username', 'employee_id'] and value else value
            print(f"   {field}: {masked_value}")
    else:
        print("\n❌ ONBOARDING WORKFLOW FAILED")

if __name__ == "__main__":
    main()
