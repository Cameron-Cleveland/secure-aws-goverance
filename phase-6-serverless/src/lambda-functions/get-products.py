import json
import boto3
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['PRODUCTS_TABLE'])

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    
    try:
        # Check if specific product ID is requested
        if event.get('pathParameters') and event['pathParameters'].get('product_id'):
            product_id = event['pathParameters']['product_id']
            response = table.get_item(Key={'product_id': product_id})
            product = response.get('Item')
            
            if product:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(product)
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Product not found'})
                }
        
        # Get all products (with optional category filter)
        query_params = event.get('queryStringParameters') or {}
        category = query_params.get('category')
        
        if category:
            response = table.query(
                IndexName='CategoryIndex',
                KeyConditionExpression=Key('category').eq(category)
            )
        else:
            response = table.scan()
        
        products = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'products': products,
                'count': len(products)
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
