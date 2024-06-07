import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    s3_client = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'))
    bucket_name = '5225pixtag-images'  # 替换为您的S3桶名称
    object_name = event['queryStringParameters']['object_name']
    expiration = 3600  # URL有效时间为1小时

    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': bucket_name, 'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'url': response})
    }
