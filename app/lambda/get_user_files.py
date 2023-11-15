# a lambda handler
import boto3
import os
import json
from botocore.client import Config


def lambda_handler(event, context):
    # get the cognito username from the event identity
    username = event['requestContext']['authorizer']['claims']['cognito:username']
    # username = "gasamoma"
    # prefix output/ with username
    username = "public/processed/" + username
    bucketname = os.environ['BUCKET_NAME']
    # get the file keys from username prefix from the s3 bucket
    s3 = boto3.client('s3',config=Config(signature_version='s3v4'))
    response = s3.list_objects_v2(Bucket=bucketname, Prefix=username)
    # get all the keys into a list 
    keys = [{'s3Key':item['Key'],"name": item['Key'].split("/")[-1] } for item in response['Contents']]
    # return only the object keys 
    # presing all using SignatureVersion4 the urls from keys and add it to the response
    for key in keys:
        key['url'] = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': bucketname, 'Key': key['s3Key']}, ExpiresIn=3600)
    
    return {
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': os.environ['CORS_ORIGIN'] if 'CORS_ORIGIN' in os.environ else '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
        'statusCode': 200,
        'body': json.dumps(keys)
        }