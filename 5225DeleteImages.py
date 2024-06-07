import json
import boto3

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('5225ImageTags')


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        image_urls = body['image_urls']

        for url in image_urls:
            # Extract bucket and key from URL
            bucket_name = url.split('//')[1].split('.')[0]
            key = '/'.join(url.split('/')[3:])

            # Delete original image and thumbnail from S3
            s3_client.delete_object(Bucket=bucket_name, Key=key)
            thumbnail_key = 'thumbnails/' + key
            s3_client.delete_object(Bucket=bucket_name, Key=thumbnail_key)

            # Delete entries from DynamoDB
            table.delete_item(
                Key={
                    'ImageURL': url
                }
            )

        return {
            'statusCode': 200,
            'body': json.dumps('Images and thumbnails deleted successfully')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
