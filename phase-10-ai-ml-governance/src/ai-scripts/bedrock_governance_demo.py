#!/usr/bin/env python3
"""
AWS BedRock Governance & Security Demo
Demonstrates AI model governance, content filtering, and responsible AI practices
"""

import boto3
import json
import logging
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedRockGovernance:
    def __init__(self):
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.bedrock = boto3.client('bedrock', region_name='us-east-1')
        self.config = boto3.client('config', region_name='us-east-1')
        
    def list_available_models(self):
        """List available foundation models with governance info"""
        try:
            response = self.bedrock.list_foundation_models()
            
            print("🔍 Available Foundation Models:")
            print("=" * 80)
            
            for model in response['modelSummaries']:
                print(f"🤖 Model: {model['modelId']}")
                print(f"   Provider: {model['providerName']}")
                print(f"   Name: {model['modelName']}")
                print(f"   Modalities: {', '.join(model['modalities'])}")
                print(f"   Customizations: {', '.join(model.get('customizationsSupported', []))}")
                print(f"   Output Modalities: {', '.join(model.get('outputModalities', []))}")
                print("-" * 40)
                
            return response['modelSummaries']
            
        except ClientError as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def get_model_details(self, model_id):
        """Get detailed information about a specific model"""
        try:
            response = self.bedrock.get_foundation_model(modelIdentifier=model_id)
            model = response['modelDetails']
            
            print(f"🔍 Detailed Model Information for {model_id}:")
            print("=" * 80)
            print(f"Model ID: {model['modelId']}")
            print(f"Model Name: {model['modelName']}")
            print(f"Provider: {model['providerName']}")
            print(f"Modalities: {', '.join(model['modalities'])}")
            print(f"Supported Customizations: {', '.join(model.get('customizationsSupported', []))}")
            print(f"Inference Types: {', '.join(model.get('inferenceTypesSupported', []))}")
            print(f"Model Lifecycle: {model.get('modelLifecycle', {}).get('status', 'Unknown')}")
            
            return model
            
        except ClientError as e:
            logger.error(f"Error getting model details: {e}")
            return None
    
    def invoke_model_with_guardrails(self, model_id, prompt):
        """Invoke a model with basic content safety checks"""
        try:
            # Basic content safety check
            if self._contains_sensitive_content(prompt):
                print("🚫 Content safety check failed: Prompt contains sensitive content")
                return None
            
            # Prepare the request body for Claude model
            if "claude" in model_id.lower():
                body = {
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": 200,
                    "temperature": 0.5,
                    "top_p": 0.9,
                }
                
                response = self.bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType='application/json',
                    accept='application/json'
                )
                
                response_body = json.loads(response['body'].read())
                return response_body.get('completion', 'No response generated')
                
            else:
                print(f"Model {model_id} invocation pattern not implemented in demo")
                return "Demo response: Model governance checks passed ✅"
                
        except ClientError as e:
            logger.error(f"Error invoking model: {e}")
            return None
    
    def _contains_sensitive_content(self, text):
        """Basic content safety check"""
        sensitive_keywords = [
            'harmful', 'dangerous', 'illegal', 'hate speech', 
            'discrimination', 'violence', 'exploit'
        ]
        
        text_lower = text.lower()
        for keyword in sensitive_keywords:
            if keyword in text_lower:
                return True
        return False
    
    def check_governance_compliance(self):
        """Check AWS Config compliance for BedRock resources"""
        try:
            response = self.config.describe_config_rules()
            
            print("🔍 AWS Config Governance Rules:")
            print("=" * 80)
            
            for rule in response['ConfigRules']:
                if 'bedrock' in rule['ConfigRuleName'].lower():
                    print(f"📋 Rule: {rule['ConfigRuleName']}")
                    print(f"   State: {rule.get('ConfigRuleState', 'Unknown')}")
                    print(f"   Source: {rule['Source']['Owner']}")
                    print("-" * 40)
                    
        except ClientError as e:
            logger.error(f"Error checking config rules: {e}")

def main():
    """Main demonstration function"""
    governance = BedRockGovernance()
    
    print("🚀 AWS BedRock Governance & Security Demo")
    print("=" * 80)
    
    # 1. List available models
    models = governance.list_available_models()
    
    if models:
        # 2. Get details for first model
        first_model = models[0]['modelId']
        governance.get_model_details(first_model)
        
        # 3. Demonstrate content safety
        print("\n🛡️ Content Safety Demonstration:")
        print("=" * 80)
        
        # Safe prompt
        safe_prompt = "Explain the benefits of renewable energy"
        print(f"Safe prompt: '{safe_prompt}'")
        response = governance.invoke_model_with_guardrails(first_model, safe_prompt)
        if response:
            print(f"Response: {response}")
        
        # Potentially unsafe prompt (demo purposes)
        unsafe_prompt = "This is a harmful and dangerous request"
        print(f"\nUnsafe prompt: '{unsafe_prompt}'")
        response = governance.invoke_model_with_guardrails(first_model, unsafe_prompt)
        if not response:
            print("✅ Content safety check correctly blocked unsafe prompt")
    
    # 4. Check governance compliance
    print("\n📊 Governance Compliance Check:")
    governance.check_governance_compliance()
    
    print("\n🎉 BedRock Governance Demo Complete!")

if __name__ == "__main__":
    main()
