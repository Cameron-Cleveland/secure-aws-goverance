#!/usr/bin/env python3
"""
Debug BedRock Response to see actual output
"""

import boto3
import json
import re

def debug_bedrock():
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    sample_data = {
        "full_name": "Maria Garcia Rodriguez",
        "email": "maria.garcia@company.com",
        "position": "Cloud Engineer",
        "department": "Cloud Infrastructure", 
        "start_date": "2024-02-01",
        "employee_id": "CE-2024-002",
        "manager": "Robert Chen"
    }
    
    prompt = f"""
Human: Extract the following information from this HR data and return as VALID JSON with these exact keys: username, email, role, start_date, department, employee_id, manager.

HR Data: {json.dumps(sample_data)}

Return ONLY valid JSON with exactly those keys, no other text.

Assistant:
"""
    
    print("🤖 Sending prompt to BedRock...")
    print("Prompt:", prompt[:200] + "..." if len(prompt) > 200 else prompt)
    
    body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 500,
            "temperature": 0.1
        }
    }
    
    response = bedrock_runtime.invoke_model(
        modelId='amazon.titan-text-express-v1',
        body=json.dumps(body)
    )
    
    response_body = json.loads(response['body'].read())
    result_text = response_body['results'][0]['outputText'].strip()
    
    print("\n📨 RAW BEDROCK RESPONSE:")
    print("=" * 50)
    print(result_text)
    print("=" * 50)
    
    # Try to extract JSON
    print("\n🔍 ATTEMPTING JSON EXTRACTION...")
    json_match = re.search(r'\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}', result_text, re.DOTALL)
    if json_match:
        json_str = json_match.group()
        print("Extracted JSON string:")
        print(json_str)
        
        try:
            parsed_data = json.loads(json_str)
            print("\n✅ SUCCESSFULLY PARSED JSON:")
            for key, value in parsed_data.items():
                print(f"  {key}: {value}")
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON PARSE ERROR: {e}")
            print("Trying to fix JSON...")
            
            # Try to fix common JSON issues
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            try:
                parsed_data = json.loads(json_str)
                print("✅ FIXED JSON:")
                for key, value in parsed_data.items():
                    print(f"  {key}: {value}")
            except json.JSONDecodeError as e2:
                print(f"❌ Still cannot parse: {e2}")
    else:
        print("❌ No JSON found in response")

if __name__ == "__main__":
    debug_bedrock()
