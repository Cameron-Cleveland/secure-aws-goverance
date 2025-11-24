import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['ORDERS_TABLE'])

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    
    try:
        # Get order_id from path parameters
        if not event.get('pathParameters') or not event['pathParameters'].get('order_id'):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Order ID is required in path parameters'})
            }
        
        order_id = event['pathParameters']['order_id']
        
        # Get order from DynamoDB
        response = table.get_item(Key={'order_id': order_id})
        order = response.get('Item')
        
        if not order:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Order not found'})
            }
        
        # Return order details (excluding sensitive fields if needed)
        order_response = {
            'order_id': order['order_id'],
            'customer_id': order['customer_id'],
            'status': order['status'],
            'total_amount': float(order['total_amount']),
            'created_at': order['created_at'],
            'items': order['items']
        }
        
        # Add shipping address if exists
        if 'shipping_address' in order:
            order_response['shipping_address'] = order['shipping_address']
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(order_response)
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
