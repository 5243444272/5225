import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('5225ImageTags')


def lambda_handler(event, context):
    response = table.scan()
    items = response['Items']

    return {
        'statusCode': 200,
        'body': json.dumps(items),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
