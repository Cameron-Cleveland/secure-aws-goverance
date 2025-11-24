import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ['ORDERS_TABLE'])
products_table = dynamodb.Table(os.environ['PRODUCTS_TABLE'])

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    
    try:
        # Parse request body
        if event.get('body'):
            body = json.loads(event['body'])
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        # Validate required fields
        required_fields = ['customer_id', 'items']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        # Validate items and calculate total
        total_amount = 0
        for item in body['items']:
            if 'product_id' not in item or 'quantity' not in item:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Each item must have product_id and quantity'})
                }
            
            # Get product price
            product_response = products_table.get_item(Key={'product_id': item['product_id']})
            if 'Item' not in product_response:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': f"Product {item['product_id']} not found"})
                }
            
            product = product_response['Item']
            item['unit_price'] = float(product['price'])
            item['total_price'] = item['unit_price'] * item['quantity']
            total_amount += item['total_price']
        
        # Create order
        order_id = str(uuid.uuid4())
        order = {
            'order_id': order_id,
            'customer_id': body['customer_id'],
            'items': body['items'],
            'total_amount': total_amount,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add shipping address if provided
        if 'shipping_address' in body:
            order['shipping_address'] = body['shipping_address']
        
        # Save order to DynamoDB
        orders_table.put_item(Item=order)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Order created successfully',
                'order_id': order_id,
                'total_amount': total_amount
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
