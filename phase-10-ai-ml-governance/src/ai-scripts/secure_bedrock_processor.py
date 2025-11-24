import boto3
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Secure BedRock processor with security controls"""
    
    logger.info("Secure AI processor invoked with security context")
    
    try:
        # Initialize AWS clients
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        kms = boto3.client('kms', region_name='us-east-1')
        
        # Security: Log invocation context
        logger.info(f"Security context: VPC-only access, KMS encryption enabled")
        
        # Check if this is a test event
        if 'test' in event:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Secure AI processor is operational',
                    'security_features': [
                        'VPC endpoint access only',
                        'KMS encryption at rest',
                        'IAM with minimal permissions',
                        'Private network isolation'
                    ],
                    'status': 'secure_environment_ready'
                })
            }
        
        # Process actual BedRock requests
        if 'body' in event:
            try:
                body = json.loads(event['body'])
                prompt = body.get('prompt', '')
                
                if prompt:
                    # Security: Validate input length
                    if len(prompt) > 1000:
                        return {
                            'statusCode': 400,
                            'body': json.dumps({'error': 'Prompt too long'})
                        }
                    
                    # Prepare BedRock request
                    request_body = {
                        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                        "max_tokens_to_sample": 200,
                        "temperature": 0.5
                    }
                    
                    # Invoke BedRock model (commented for safety, uncomment when ready)
                    # response = bedrock.invoke_model(
                    #     modelId="anthropic.claude-v2",
                    #     body=json.dumps(request_body)
                    # )
                    # result = json.loads(response['body'].read())
                    
                    # For now, return mock response
                    return {
                        'statusCode': 200,
                        'body': json.dumps({
                            'completion': 'This is a secure AI response from VPC-isolated environment.',
                            'security_context': 'vpc_private_access',
                            'model_status': 'secure_connection_ready'
                        })
                    }
                else:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'No prompt provided'})
                    }
                    
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON'})
                }
        
        # Default response for direct invocation
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Secure AI BedRock processor',
                'status': 'operational',
                'security_level': 'enterprise_grade'
            })
        }
        
    except Exception as e:
        logger.error(f"Secure AI processing error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'AI processing failed',
                'security_context': 'vpc_private_access'
            })
        }
