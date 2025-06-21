import json
import boto3
import uuid
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    user_id = event.get('pathParameters', {}).get('user_id')

    if http_method == 'POST' and path == '/users':
        body = json.loads(event['body'])
        return create_user(body)

    elif http_method == 'GET' and user_id:
        return get_user(user_id)

    elif http_method == 'PUT' and user_id:
        body = json.loads(event['body'])
        return update_user(user_id, body)

    elif http_method == 'DELETE' and user_id:
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
    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'User created', 'user_id': user_id})
    }

def get_user(user_id):
    response = table.get_item(Key={'user_id': user_id})
    item = response.get('Item')
    if not item:
        return {'statusCode': 404, 'body': json.dumps({'message': 'User not found'})}
    return {'statusCode': 200, 'body': json.dumps(item)}

def update_user(user_id, data):
    update_expression = []
    expression_values = {}
    expression_names = {}

    if 'name' in data:
        update_expression.append("#n = :n")
        expression_values[':n'] = data['name']
        expression_names['#n'] = 'name'

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
        table.delete_item(
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
