import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('5225ImageTags')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        image_url = body['image_url']
        tags_to_remove = set(body['tags'])

        # 获取当前标签
        response = table.get_item(Key={'ImageURL': image_url})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps('Image not found')
            }

        current_tags = set(response['Item']['Tags'])

        # 更新标签
        updated_tags = list(current_tags - tags_to_remove)
        table.update_item(
            Key={'ImageURL': image_url},
            UpdateExpression="SET Tags = :updated_tags",
            ExpressionAttributeValues={':updated_tags': updated_tags},
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'body': json.dumps('Tags updated successfully')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
