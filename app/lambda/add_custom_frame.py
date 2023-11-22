import json
import urllib.parse
import boto3
import base64
import io
from PIL import Image, ImageOps
import numpy as np
from io import BytesIO
import requests
import os
import re

#clients
s3 = boto3.client('s3')
basewidth = 512+30+30
hsize = 512+120+30

attributes = {'key'}

headers = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ['CORS_ORIGIN'] if 'CORS_ORIGIN' in os.environ else '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

def lambda_handler(event, context):
    bucket = os.environ['BUCKET']
    # get the key of the new object in s3 event
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    frame_img = os.environ.get("FRAME_KEY","public/marco_girls.png")
    image_data = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    
    img_fondo = s3.get_object(Bucket=bucket, Key=frame_img)["Body"].read()
    img_fondo = Image.open(BytesIO(img_fondo))
    img = Image.open(BytesIO(image_data))
    img = ImageOps.expand(img, border=(30, 30, 30, 120), fill="white")
    img_fondo = img_fondo.resize((basewidth, hsize))
    img_fondo.convert("RGBA")
    img.convert("RGBA")
    arr = np.array(img_fondo)
    arr[:, :, 3] = (arr[:, :, :3] != 255).any(axis=2) * 255
    fondo = Image.fromarray(arr, mode='RGBA')
    img.paste(fondo, (0, 0), fondo)
    # Save the image to an in-memory file
    in_mem_file = io.BytesIO()
    img.save(in_mem_file, format='jpeg', quality=95)
    in_mem_file.seek(0)
    # replace key unprocessed with processed
    key = re.sub(r'unprocessed/', r'processed/', key)
    print(key)
    s3.upload_fileobj(in_mem_file, bucket, key)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }