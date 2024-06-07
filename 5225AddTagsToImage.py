import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('5225ImageTags')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        image_url = body['image_url']
        new_tags = body['tags']

        # 更新DynamoDB中的标签
        response = table.update_item(
            Key={'ImageURL': image_url},
            UpdateExpression="SET Tags = list_append(Tags, :new_tags)",
            ExpressionAttributeValues={':new_tags': new_tags},
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'body': json.dumps(response['Attributes'])
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
