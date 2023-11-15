import json
import urllib.parse
import boto3
import base64
import io
from io import BytesIO
import requests
import os
import re

#clients
s3 = boto3.client('s3')
client_topic = boto3.client('iot-data', region_name='us-east-1')
modelId = os.environ.get("MODELID",'stability.stable-diffusion-xl-v0')
GENDERMAP= {"Male" : "Man", "Female" : "Woman"}
ROOP = "http://"+os.environ.get("ROOP","internal-roop-internal-1518407261.us-east-1.elb.amazonaws.com")+'/start_roop'
topic = 'StyleGenerated'

rekognition = boto3.client('rekognition', endpoint_url="https://rekognition.us-east-1.amazonaws.com")
sts_client =  boto3.client('sts', endpoint_url='https://sts.us-east-1.amazonaws.com')
basewidth = 512+30+30
hsize = 512+120+30

attributes = {'key'}
styles = {1: {'name': 'Biologist', 'prompt': 'Woman, inquisitive expression, biologist, laboratory setting, microscope, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, biological research, analyzing pose, laboratory tools in hands, curious, Hyper realistic.'}, 2: {'name': 'Chemist', 'prompt': 'Woman, focused expression, chemist, chemical laboratory, test tubes, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, chemical analysis, experimenting pose, lab equipment in hands, precise, Hyper realistic.'}, 3: {'name': 'Physicist', 'prompt': 'Woman, contemplative expression, physicist, research facility, particle accelerator, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, theoretical physics, pondering pose, scientific equipment in hands, analytical, Hyper realistic.'}, 4: {'name': 'Astronomer', 'prompt': 'Woman, awe-struck expression, astronomer, observatory setting, telescope, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, celestial observation, stargazing pose, telescope in hands, fascinated, Hyper realistic.'}, 5: {'name': 'Geologist', 'prompt': 'Woman, adventurous expression, geologist, fieldwork setting, rock formations, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, geological exploration, examining pose, geological tools in hands, determined, Hyper realistic.'}, 6: {'name': 'Ecologist', 'prompt': 'Woman, environmentalist expression, ecologist, natural habitat setting, wildlife observation, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, ecological study, observing pose, environmental tools in hands, passionate, Hyper realistic.'}, 7: {'name': 'Microbiologist', 'prompt': 'Woman, focused expression, microbiologist, laboratory setting, petri dish, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, microbiological research, examining pose, laboratory tools in hands, meticulous, Hyper realistic.'}, 8: {'name': 'Neuroscientist', 'prompt': 'Woman, thoughtful expression, neuroscientist, brain research lab, EEG equipment, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, neuroscience study, analyzing pose, scientific tools in hands, thoughtful, Hyper realistic.'}, 9: {'name': 'Geneticist', 'prompt': 'Woman, analytical expression, geneticist, DNA research lab, double helix model, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, genetic research, studying pose, laboratory tools in hands, analytical, Hyper realistic.'}, 10: {'name': 'Environmental Scientist', 'prompt': 'Woman, environmentally conscious expression, environmental scientist, fieldwork setting, ecological monitoring, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, environmental research, monitoring pose, scientific tools in hands, conscientious, Hyper realistic.'}, 11: {'name': 'Software Developer', 'prompt': 'Woman, focused expression, software developer, coding environment, computer setup, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, coding expertise, coding pose, laptop in hands, innovative, Hyper realistic.'}, 12: {'name': 'Data Scientist', 'prompt': 'Woman, analytical expression, data scientist, analyzing data, visualizations, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, data analysis, interpreting pose, analytics tools in hands, precise, Hyper realistic.'}, 13: {'name': 'Network Engineer', 'prompt': 'Woman, determined expression, network engineer, server room, networking equipment, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, network management, configuring pose, networking tools in hands, focused, Hyper realistic.'}, 14: {'name': 'Cybersecurity Analyst', 'prompt': 'Woman, vigilant expression, cybersecurity analyst, security operations center, monitoring screens, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, cybersecurity, monitoring pose, security tools in hands, alert, Hyper realistic.'}, 15: {'name': 'Database Administrator', 'prompt': 'Woman, organized expression, database administrator, database management, SQL queries, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, database administration, organizing pose, database tools in hands, efficient, Hyper realistic.'}, 16: {'name': 'UX-UI Designer', 'prompt': 'Woman, creative expression, UX/UI designer, design studio setting, wireframes, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, user experience design, designing pose, design tools in hands, creative, Hyper realistic.'}, 17: {'name': 'IT Project Manager', 'prompt': 'Woman, leadership expression, IT project manager, project management office, Gantt chart, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, project management, overseeing pose, project documents in hands, decisive, Hyper realistic.'}, 18: {'name': 'Civil Engineer', 'prompt': 'Woman, confident expression, civil engineer, construction site, blueprint, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, civil engineering, planning pose, construction tools in hands, determined, Hyper realistic.'}, 19: {'name': 'Mechanical Engineer', 'prompt': 'Woman, hands-on expression, mechanical engineer, workshop setting, machinery, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, mechanical engineering, designing pose, mechanical tools in hands, skilled, Hyper realistic.'}, 20: {'name': 'Electrical Engineer', 'prompt': 'Woman, focused expression, electrical engineer, electronics lab, circuit board, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, electrical engineering, testing pose, electronic tools in hands, precise, Hyper realistic.'}, 21: {'name': 'Aerospace Engineer', 'prompt': 'Woman, determined expression, aerospace engineer, aircraft hangar, designing aircraft, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, aerospace engineering, analyzing pose, aircraft tools in hands, innovative, Hyper realistic.'}, 22: {'name': 'Biomedical Engineer', 'prompt': 'Woman, compassionate expression, biomedical engineer, medical research lab, biomedical devices, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, biomedical engineering, researching pose, medical tools in hands, empathetic, Hyper realistic.'}, 23: {'name': 'Environmental Engineer', 'prompt': 'Woman, environmentally conscious expression, environmental engineer, eco-friendly project, sustainable solutions, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, environmental engineering, planning pose, eco-friendly tools in hands, conscientious, Hyper realistic.'}, 24: {'name': 'Mathematician', 'prompt': 'Woman, analytical expression, mathematician, mathematical research, equations, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, mathematical exploration, pondering pose, mathematical tools in hands, insightful, Hyper realistic.'}, 25: {'name': 'Statistician', 'prompt': 'Woman, analytical expression, statistician, statistical analysis, graphs, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, statistical research, analyzing pose, statistical tools in hands, precise, Hyper realistic.'}, 26: {'name': 'Cryptographer', 'prompt': 'Woman, cryptic expression, cryptographer, encryption algorithms, codebreaking, Canon 5D Mark IV, professional photorealistic scenario, Realistic, proportioned, Cinematic, cryptography, decoding pose, cryptographic tools in hands, cryptic, Hyper realistic.'},27: {'name': 'Architect', 'prompt': 'Woman, visionary expression, architect, architectural workspace, design tools, Canon EOS R5, skilled photographer, Realistic, proportioned, Cinematic, architectural design, drawing pose, blueprint in hands, innovative, Hyper realistic.'},28: {'name': 'Scientist-Researcher', 'prompt': 'Woman, curious expression, scientist/researcher, laboratory setting, scientific equipment, Leica Q2, skilled photographer, Realistic, proportioned, Cinematic, scientific exploration, researching pose, equipment in hands, analytical, Hyper realistic.'}, 29: {'name': 'Graphic Designer', 'prompt': 'Woman, creative expression, graphic designer, design studio, Adobe Creative Cloud tools, Wacom Intuos, skilled photographer, Realistic, proportioned, Cinematic, design prowess, creating pose, graphic tablet in hands, imaginative, Hyper realistic.'},30: {'name': 'Teacher', 'prompt': 'Woman, nurturing expression, teacher, classroom setting, educational materials, Sony A6400, skilled photographer, Realistic, proportioned, Cinematic, educational passion, teaching pose, books in hands, inspiring, Hyper realistic.'}, 31: {'name': 'Psychologist', 'prompt': 'Woman, empathetic expression, psychologist, therapy setting, counseling room, Psychology Today, skilled photographer, Realistic, proportioned, Cinematic, psychological expertise, listening pose, notepad in hands, empathetic, Hyper realistic.'},32: {'name': 'Veterinarian', 'prompt': 'Woman, caring expression, veterinarian, veterinary clinic, treating animals, Nikon D5600, skilled photographer, Realistic, proportioned, Cinematic, veterinary care, caring pose, medical tools in hands, nurturing, Hyper realistic.'}}
#  add Arquitecto, Scientist, Graphic Designer, Teacher, Doctor, Psychologist, veterinarian
# prepared_prompts = {
# 'Spartan' : {
# 'Female': 'Woman, beautiful face, smiling, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, spartan greek warrior, mountain isle background, epic pose, weapon in arms, muscular, realistic, proportioned, Hyper realistic',
# 'Male': 'a front looking upper body spartan warrior from 300 movie, face visible, chest visible, in battlefield, Canon 5D Mark IV, professional photographer,  Cinematic, epic pose, weapon in arms, muscular, proportioned, Hyper realistic',  
# 'Neutral' : 'person, smiling, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, spartan greek warrior, mountain isle background, epic pose, weapon in arms, muscular, realistic, proportioned, Hyper realistic'
# },
# 'Rome' : {
# 'Male': 'man, toga, short hair, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, ancient rome, Rome background,  realistic, proportioned, Hyper realistic',
# 'Female': 'woman, beautiful, proportioned face, toga, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, ancient rome, Rome background,  realistic, proportioned, Hyper realistic',
# 'Neutral' : 'person, toga, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, ancient rome, Rome background,  realistic, proportioned, Hyper realistic'
# },
# 'StarWars' : {
# 'Male': 'Man, Star Wars, Jedi, beautiful, proportioned face, toga, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, space background, stars,  realistic, proportioned, Hyper realistic',
# 'Female' : 'Woman, Star Wars, Jedi, beautiful, proportioned face, toga, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, space background, stars,  realistic, proportioned, Hyper realistic',
# 'Neutral' : 'person, Star Wars, Jedi, beautiful, proportioned face, toga, photograph, shaven, Canon 5D Mark IV, professional photographer,  Cinematic, space background, stars,  realistic, proportioned, Hyper realistic'
# },
# 'Marvel' : {
# 'Female' : 'Marvel Movies, Woman, Canon 5D Mark IV, professional photographer,  Cinematic,  New York, background, epic pose, weapon in arms, muscular, realistic, proportioned, Hyper realistic',
# 'Male' : 'Marvel Movies, Man, Canon 5D Mark IV, professional photographer,  Cinematic,  New York, background, epic pose, weapon in arms, muscular, realistic, proportioned, Hyper realistic',
# 'Neutral' : 'Marvel Movies, Person, Canon 5D Mark IV, professional photographer,  Cinematic,  New York, background, epic pose, weapon in arms, muscular, realistic, proportioned, Hyper realistic',
# }
# }
negative_prompt = 'helmet, armor, Watermark, Text, censored, deformed, bad anatomy, disfigured, poorly drawn face, mutated, extra limb, ugly, poorly drawn hands, missing limb, floating limbs, disconnected limbs, disconnected head, malformed hands, long neck, mutated hands and fingers, bad hands, missing fingers, cropped, worst quality, low quality, mutation, poorly drawn, huge calf, bad hands, fused hand, missing hand, disappearing arms, disappearing thigh, disappearing calf, disappearing legs, missing fingers, fused fingers, abnormal eye proportion, Abnormal hands, abnormal legs, abnormal feet,  abnormal fingers, camera, camera on hand, camera repesentation, multiple faces, face not visible,eyes not visible'# avoid multiple focused faces
headers = {
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Origin': os.environ['CORS_ORIGIN'] if 'CORS_ORIGIN' in os.environ else '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    } 
def detect_faces(bucket, key):
    age_gender = {'Age' : 16, 'Gender': 'Female'}
    # try:
    #     response = rekognition.detect_faces(Image={'S3Object' : { 'Bucket': bucket, 'Name': key }}, Attributes=['AGE_RANGE', 'GENDER'])
    #     face = response['FaceDetails'][0]
    #     age_gender['Gender'] = face['Gender']['Value']
    #     age_gender['Age'] = face['AgeRange']['Low']
    # except :
    #     print("Couldn't detect faces in image" ) 
    #     pass
    return age_gender



def publish_message(topic2, mensaje):
    return None
    # llave='imageKey'
    # response = client_topic.publish(
    #     topic=topic2,
    #     qos=1,
    #     payload=json.dumps({llave : mensaje})
    # )
    # print(response)

def clean_user_input(user_input):
    custom_name = user_input
    custom_name = custom_name.lower()
    custom_name = custom_name.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    custom_name = custom_name.title()
    custom_name = re.sub(r'[^a-zA-Z0-9]+', '', custom_name)
    return custom_name

clean_user_input("PílAr A.lexandrá")

def lambda_handler(event, context):
    # get the cognito username from the event
    username = event['requestContext']['authorizer']['claims']['cognito:username']
    
    body = json.loads(event['body'])
    bucket = os.environ.get("BUCKET", None)
    # if bucket is none return 404
    if  bucket is None:
        return {
            'statusCode': 404,
            'body': json.dumps('Bucket not found'),
            'headers': headers
        }
    key = urllib.parse.unquote_plus(body['key'], encoding='utf-8')
    style = styles[int(body['styles'])]
    custom_name = clean_user_input(body['custom-name'])
    
    bedrock = boto3.client('bedrock-runtime')
    s3_object = s3.get_object(Bucket=bucket, Key=key)
    file_byte_string = s3_object['Body'].read()
    photo_data = BytesIO(file_byte_string)
    
    print("Got Object")
    age_gender = detect_faces(bucket, key)
    print("Called Rekognition")
    prompt_data = style['prompt']
    style_name = style['name']
    # prompt_data = prepared_prompts.get(style).get(age_gender['Gender']) 
    print(prompt_data)
    body = json.dumps({"text_prompts":[{"text": prompt_data },{"text" : negative_prompt, "weight" : -0.9}], "steps":50 ,"cfg_scale":10, "samples" : 1 , "style_preset" : 'photographic' })
    try: 
        response = bedrock.invoke_model(body=body, modelId=modelId, contentType="application/json", accept="image/png")
    except Exception as error:
        print(error)
        raise error
    print("Called Bedrock")
    if response['contentType'] == 'image/png':
        print("got PNG")
        image_data = response['body'].read()
    else:
        print("NOT PNG")
        image_data = response['body']
        print(image_data)

    
    #nombre = key.split("/")
    print("got files")
    multiple_files = [('src_file', ('1.jpg', photo_data)),
                      ('target_file', ('2.jpg', image_data))]
    print("Posted to Roop")
    response = requests.post(url=ROOP, files=multiple_files) 
    print("Got Response from Roop")
    bin_data = response.content
    # if response status code is not 200 range
    if response.status_code != 200:
        publish_message(topic, 'ERROR')
        raise response.status_code
    try:
        # remove the file extention from the key
        key_no_ext = ((key.split('/'))[-1]).split('.')[0]
        nuevaKey= "public/processed/"+username+"/"+style_name+"-"+custom_name+".jpeg"
        print(nuevaKey)
        # Upload image to s3
        s3.put_object(Bucket=bucket,
                     Key=nuevaKey,
                     Body=bin_data,
                     ContentType='image/jpeg')
        # presign nueva key for view  object in browser
        url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': bucket, 'Key': nuevaKey}, ExpiresIn=3600)
        # return the lamnda response with the url
        return {
            'headers': headers,
            'statusCode': 200,
            'body': json.dumps({'presigned_url_processed':url})
        }
        print("imagen generada guardada ! ")
    except Exception as e:
        print(e)
        print('Error putting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
        publish_message(topic,'ERROR')
        return {"ok" : "ok"}