import boto3
import json
import cv2
import numpy as np
from urllib.parse import unquote_plus
from concurrent.futures import ThreadPoolExecutor

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')
table = dynamodb.Table('5225ImageTags')
sns_topic_arn = 'arn:aws:sns:us-east-1:875780883286:ImageTagNotifications' 

def download_file_from_s3(bucket, key, download_path):
    s3_client.download_file(bucket, key, download_path)

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'])

    try:
        download_path = '/tmp/{}'.format(key)
        s3_client.download_file(bucket, key, download_path)
    except Exception as e:
        print(f"Error downloading file from bucket {bucket} with key {key}: {str(e)}")
        raise e

    yolov3_cfg_path = '/tmp/yolov3-tiny.cfg'
    yolov3_weights_path = '/tmp/yolov3-tiny.weights'
    coco_names_path = '/tmp/coco.names'

    with ThreadPoolExecutor() as executor:
        executor.submit(download_file_from_s3, '5225pixtag-images', 'yolov3-tiny.cfg', yolov3_cfg_path)
        executor.submit(download_file_from_s3, '5225pixtag-images', 'yolov3-tiny.weights', yolov3_weights_path)
        executor.submit(download_file_from_s3, '5225pixtag-images', 'coco.names', coco_names_path)

    image = cv2.imread(download_path)
    thumbnail = cv2.resize(image, (128, 128))
    thumbnail_path = '/tmp/thumbnail-{}'.format(key)
    cv2.imwrite(thumbnail_path, thumbnail)

    thumbnail_key = 'thumbnails/{}'.format(key)
    s3_client.upload_file(thumbnail_path, bucket, thumbnail_key)

    net = cv2.dnn.readNet(yolov3_weights_path, yolov3_cfg_path)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    with open(coco_names_path, "r") as f:
        classes = [line.strip() for line in f.readlines()]

    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    tags = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.6:
                tag = classes[class_id]
                if tag not in tags:
                    tags.append(tag)

    s3_url = "https://{}.s3.amazonaws.com/{}".format(bucket, key)
    table.put_item(
        Item={
            'ImageURL': s3_url,
            'Tags': tags
        }
    )

    message = f"New image uploaded with tags: {', '.join(tags)}. URL: {s3_url}"
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=message,
        Subject="New Image Tag Notification"
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Tags stored and notification sent successfully')
    }
