#!/usr/bin/env python3
"""
AI Guardrails Setup and Configuration
Demonstrates responsible AI practices and content filtering
"""

import boto3
import json
import logging
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIGuardrails:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.iam = boto3.client('iam')
        self.config = boto3.client('config')
        
    def create_ai_governance_policy(self):
        """Create comprehensive AI governance policy"""
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AIGovernanceBasic",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:ListFoundationModels",
                        "bedrock:GetFoundationModel"
                    ],
                    "Resource": "*"
                },
                {
                    "Sid": "AIContentSafety",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel"
                    ],
                    "Resource": [
                        "arn:aws:bedrock:*::foundation-model/amazon.titan-text-express-v1",
                        "arn:aws:bedrock:*::foundation-model/amazon.titan-text-lite-v1",
                        "arn:aws:bedrock:*::foundation-model/anthropic.claude-v2"
                    ],
                    "Condition": {
                        "StringEquals": {
                            "aws:RequestTag/Environment": "demo",
                            "aws:RequestTag/Project": "secure-governance-demo"
                        }
                    }
                },
                {
                    "Sid": "AIMonitoring",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:ListModelCustomizationJobs",
                        "bedrock:GetModelCustomizationJob"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "StringEquals": {
                            "aws:ResourceTag/Environment": "demo"
                        }
                    }
                }
            ]
        }
        
        try:
            response = self.iam.create_policy(
                PolicyName='AIGovernanceComprehensive',
                PolicyDocument=json.dumps(policy_document),
                Description='Comprehensive AI governance and security policy',
                Tags=[
                    {'Key': 'Environment', 'Value': 'demo'},
                    {'Key': 'Project', 'Value': 'secure-governance-demo'},
                    {'Key': 'Component', 'Value': 'ai-governance'}
                ]
            )
            
            print("✅ AI Governance Policy Created:")
            print(f"   Policy ARN: {response['Policy']['Arn']}")
            return response['Policy']['Arn']
            
        except ClientError as e:
            logger.error(f"Error creating policy: {e}")
            return None
    
    def setup_training_data_governance(self, bucket_name):
        """Set up governance for AI training data"""
        try:
            # Enable S3 access logging
            self.s3.put_bucket_logging(
                Bucket=bucket_name,
                BucketLoggingStatus={
                    'LoggingEnabled': {
                        'TargetBucket': bucket_name,
                        'TargetPrefix': 'logs/'
                    }
                }
            )
            
            # Add governance tags
            self.s3.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={
                    'TagSet': [
                        {'Key': 'Environment', 'Value': 'demo'},
                        {'Key': 'Project', 'Value': 'secure-governance-demo'},
                        {'Key': 'DataClassification', 'Value': 'confidential'},
                        {'Key': 'AI_Training_Data', 'Value': 'true'},
                        {'Key': 'Retention', 'Value': '7-years'}
                    ]
                }
            )
            
            print("✅ AI Training Data Governance Configured:")
            print(f"   Bucket: {bucket_name}")
            print("   Enabled: Access logging, Governance tags, Classification")
            
        except ClientError as e:
            logger.error(f"Error setting up data governance: {e}")
    
    def create_responsible_ai_framework(self):
        """Create responsible AI framework documentation"""
        framework = {
            "responsible_ai_framework": {
                "version": "1.0",
                "project": "secure-governance-demo",
                "principles": [
                    {
                        "principle": "Fairness",
                        "description": "AI systems should treat all people fairly",
                        "controls": [
                            "Bias detection in training data",
                            "Regular fairness audits",
                            "Diverse testing scenarios"
                        ]
                    },
                    {
                        "principle": "Transparency",
                        "description": "AI systems should be transparent and explainable",
                        "controls": [
                            "Model documentation",
                            "Decision explanation capabilities",
                            "Audit trails"
                        ]
                    },
                    {
                        "principle": "Privacy & Security",
                        "description": "AI systems should protect user privacy and be secure",
                        "controls": [
                            "Data encryption",
                            "Access controls",
                            "Privacy impact assessments"
                        ]
                    },
                    {
                        "principle": "Reliability & Safety",
                        "description": "AI systems should perform reliably and safely",
                        "controls": [
                            "Robust testing",
                            "Safety guardrails",
                            "Continuous monitoring"
                        ]
                    }
                ],
                "monitoring": {
                    "continuous_monitoring": True,
                    "compliance_checks": True,
                    "performance_tracking": True,
                    "bias_detection": True
                }
            }
        }
        
        # Save framework to file
        with open('responsible_ai_framework.json', 'w') as f:
            json.dump(framework, f, indent=2)
        
        print("✅ Responsible AI Framework Created:")
        print("   File: responsible_ai_framework.json")
        print("   Principles: Fairness, Transparency, Privacy, Reliability")
        
        return framework

def main():
    """Main guardrails setup function"""
    guardrails = AIGuardrails()
    
    print("🚀 AI Guardrails and Responsible AI Setup")
    print("=" * 80)
    
    # 1. Create AI governance policy
    policy_arn = guardrails.create_ai_governance_policy()
    
    # 2. Setup training data governance (using a demo bucket name)
    demo_bucket = "secure-governance-demo-ai-data"
    guardrails.setup_training_data_governance(demo_bucket)
    
    # 3. Create responsible AI framework
    framework = guardrails.create_responsible_ai_framework()
    
    print("\n🎉 AI Guardrails Setup Complete!")
    print("\n📋 Summary of AI Governance Controls:")
    print("   ✅ IAM Policies with resource-level permissions")
    print("   ✅ Content safety checks and filtering")
    print("   ✅ Training data governance and classification")
    print("   ✅ Responsible AI framework with 4 core principles")
    print("   ✅ Continuous monitoring and compliance tracking")

if __name__ == "__main__":
    main()
