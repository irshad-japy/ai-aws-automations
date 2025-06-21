"""
python api_gateway_poc/rest_api_lambda_dynamodb.py
or
python -m api_gateway_poc.rest_api_lambda_dynamodb
"""

import json
import boto3
import uuid
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    user_id = event.get('pathParameters', {}).get('user_id')
    
    if http_method == 'POST' and path == '/users':
        body = json.loads(event['body'])
        return create_user(body)
    
    if http_method == 'GET' and user_id:
        return get_user(user_id)
    
    if http_method == 'PUT' and user_id:
        body = json.loads(event['body'])
        return update_user(user_id, body)
    
    if http_method == 'DELETE' and user_id:
        return delete_user(user_id)
    
    return {
        'statusCode': 400,
        'body': json.dumps({'message': 'Invalid request'})
    }

def create_user(data):
    user_id = str(uuid.uuid4())
    item = {
        'user_id': user_id,
        'name': data.get('name'),
        'email': data.get('email')
    }
    table.put_item(Item=item)
    return user_id  # 🔥 Return plain user_id string

def get_user(user_id):
    response = table.get_item(Key={'user_id': user_id})
    item = response.get('Item')
    if not item:
        return {'statusCode': 404, 'body': json.dumps({'message': 'User not found'})}
    return {'statusCode': 200, 'body': json.dumps(item)}

def update_user(user_id, data):
    # Check if data contains fields to update
    update_expression = []
    expression_values = {}
    expression_names = {}
    
    if 'name' in data:
        update_expression.append("#n = :n")
        expression_values[':n'] = data['name']
        expression_names['#n'] = 'name'  # Handle reserved words
    
    if 'email' in data:
        update_expression.append("#e = :e")
        expression_values[':e'] = data['email']
        expression_names['#e'] = 'email'
    
    if not update_expression:
        return {'statusCode': 400, 'body': json.dumps({'message': 'No data to update'})}
    
    update_expr = "SET " + ", ".join(update_expression)
    
    try:
        table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
        return {'statusCode': 200, 'body': json.dumps({'message': 'User updated'})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'message': f'Update failed: {str(e)}'})}


def delete_user(user_id):
    try:
        response = table.delete_item(
            Key={'user_id': user_id},
            ConditionExpression="attribute_exists(user_id)"
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'User deleted successfully'})
        }
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'User not found'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error deleting user: {str(e)}'})
        }


if __name__ == "__main__":
    # print("Creating a user...")
    user_data = {"name": "Charls", "email": "charls@example.com"}
    user_id  = "dd4d335a-0d66-4def-b26a-b66c01121636"
    
    # user_id = create_user(user_data)
    # print(f"User created with ID: {user_id}")

    
    # result = get_user(user_id)
    # print("Response:", json.dumps(result, indent=4))
    
    # update_data = {"name": "Charles Updated"}
    # Call update_user function
    # response = update_user(user_id, update_data)
    # print("Update Response:", json.dumps(response, indent=4))


    print(f"Getting details for user ID: {user_id}")
    result = get_user(user_id)
    print("User Details:", json.dumps(result, indent=4))
    
    # delete user
    delete_user(user_id)
    print("User deleted successfully")
    
    # Get user to verify update
    print(f"Getting details for user ID: {user_id}")
    result = get_user(user_id)
    print("Verify User Details:", json.dumps(result, indent=4))