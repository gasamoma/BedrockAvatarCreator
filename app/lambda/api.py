import json
import urllib.parse
import boto3
import base64
from PIL import Image, ImageOps
from pil_s3 import S3Images
import io
from io import BytesIO
import requests
​
#clients
s3 = boto3.client('s3')
client_topic = boto3.client('iot-data', region_name='us-east-1')
modelId = 'stability.stable-diffusion-xl'
GENDERMAP= {"Male" : "Man", "Female" : "Woman"}
ROOP = "http://internal-roop-internal-1518407261.us-east-1.elb.amazonaws.com/start_roop" 
topic = 'StyleGenerated'
​
images = S3Images()
rekognition = boto3.client('rekognition', endpoint_url="https://rekognition.us-east-1.amazonaws.com")
sts_client =  boto3.client('sts', endpoint_url='https://sts.us-east-1.amazonaws.com')
basewidth = 512+30+30
hsize = 512+120+30
​
attributes = {'key'}
​
prepared_prompts = {
'Spartan' : {
'Female': 'Woman, beautiful face, smiling, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, spartan greek warrior, mountain isle background, epic pose, weapon in arms, muscular, realistic, proportioned, Hyper realistic',
'Male': 'a front looking upper body spartan warrior from 300 movie, face visible, chest visible, in battlefield, Canon 5D Mark IV, professional photographer,  Cinematic, epic pose, weapon in arms, muscular, proportioned, Hyper realistic',  
'Neutral' : 'person, smiling, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, spartan greek warrior, mountain isle background, epic pose, weapon in arms, muscular, realistic, proportioned, Hyper realistic'
},
'Rome' : {
'Male': 'man, toga, short hair, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, ancient rome, Rome background,  realistic, proportioned, Hyper realistic',
'Female': 'woman, beautiful, proportioned face, toga, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, ancient rome, Rome background,  realistic, proportioned, Hyper realistic',
'Neutral' : 'person, toga, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, ancient rome, Rome background,  realistic, proportioned, Hyper realistic'
},
'StarWars' : {
'Male': 'Man, Star Wars, Jedi, beautiful, proportioned face, toga, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, space background, stars,  realistic, proportioned, Hyper realistic',
'Female' : 'Woman, Star Wars, Jedi, beautiful, proportioned face, toga, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, space background, stars,  realistic, proportioned, Hyper realistic',
'Neutral' : 'person, Star Wars, Jedi, beautiful, proportioned face, toga, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, space background, stars,  realistic, proportioned, Hyper realistic'
},
'Marvel' : {
'Female' : 'Marvel Movies, Woman, Canon 5D Mark IV, professional photographer,  Cinematic,  New York, background, epic pose, weapon in arms, muscular, realistic, proportioned, Hyper realistic',
'Male' : 'Marvel Movies, Man, Canon 5D Mark IV, professional photographer,  Cinematic,  New York, background, epic pose, weapon in arms, muscular, realistic, proportioned, Hyper realistic',
'Neutral' : 'Marvel Movies, Person, Canon 5D Mark IV, professional photographer,  Cinematic,  New York, background, epic pose, weapon in arms, muscular, realistic, proportioned, Hyper realistic',
}
}
negative_prompt = 'helmet, armor, Watermark, Text, censored, deformed, bad anatomy, disfigured, poorly drawn face, mutated, extra limb, ugly, poorly drawn hands, missing limb, floating limbs, disconnected limbs, disconnected head, malformed hands, long neck, mutated hands and fingers, bad hands, missing fingers, cropped, worst quality, low quality, mutation, poorly drawn, huge calf, bad hands, fused hand, missing hand, disappearing arms, disappearing thigh, disappearing calf, disappearing legs, missing fingers, fused fingers, abnormal eye proportion, Abnormal hands, abnormal legs, abnormal feet,  abnormal fingers'
​
def detect_faces(bucket, key):
    age_gender = {'Age' : 25, 'Gender': 'Neutral'}
    try:
        response = rekognition.detect_faces(Image={'S3Object' : { 'Bucket': bucket, 'Name': key }}, Attributes=['AGE_RANGE', 'GENDER'])
        face = response['FaceDetails'][0]
        age_gender['Gender'] = face['Gender']['Value']
        age_gender['Age'] = face['AgeRange']['Low']
    except :
        print("Couldn't detect faces in image" ) 
        pass
    return age_gender
​
​
​
def publish_message(topic2, mensaje):
    llave='imageKey'
    response = client_topic.publish(
        topic=topic2,
        qos=1,
        payload=json.dumps({llave : mensaje})
    )
    print(response)
​
​
​
def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    assumed_role_object=sts_client.assume_role(RoleArn="arn:aws:iam::479225850607:role/bedrock-crossaccount-role", RoleSessionName="LambdaRole")
    credentials=assumed_role_object['Credentials']
    bedrock = boto3.client(service_name='bedrock',region_name='us-east-1',endpoint_url='https://bedrock.us-east-1.amazonaws.com', aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'], aws_session_token=credentials['SessionToken'])
    print("Assumed Role")
    style, photo_data = images.from_s3(bucket, key)
    print("Got Object")
    age_gender = detect_faces(bucket, key)
    print("Called Rekognition")
    prompt_data = prepared_prompts.get(style).get(age_gender['Gender']) 
    print(prompt_data)
    body = json.dumps({"text_prompts":[{"text": prompt_data },{"text" : negative_prompt, "weight" : -0.9}], "steps":50 ,"cfg_scale":10, "samples" : 1 , "style_preset" : 'photographic' })
    try: 
        response = bedrock.invoke_model(body=body, modelId=modelId, contentType="application/json", accept="image/png")
    except Exception as error:
        print(error)
        raise error
    print("Called Bedrock")
    if response['contentType'] == 'image/png':
        image_data = response['body'].read()
    else:
        image_data = response['body']
​
    
    #nombre = key.split("/")
    print("got files")
    multiple_files = [('src_file', ('1.jpg', photo_data)),
                      ('target_file', ('2.jpg', image_data))]
    print("Posted to Roop")
    response = requests.post(url=ROOP, files=multiple_files) 
    print("Got Response from Roop")
    bin_data = response.content
    try:
        nuevaKey= "public/processed/" + (key.split('/'))[-1].replace(".png", ".jpeg")
        print(nuevaKey)
        # Upload image to s3
        s3.put_object(Bucket='cloud-exp-genia-2023142244-main',
                     Key=nuevaKey,
                     Body=bin_data)
        publish_message(topic, "processed/" + (key.split('/'))[-1].replace(".png", ".jpeg")) 
        print("imagen generada guardada ! ")
    except Exception as e:
        print(e)
        print('Error putting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
        publish_message(topic,'ERROR')
        return {"ok" : "ok"}