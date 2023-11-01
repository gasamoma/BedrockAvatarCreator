import json
import urllib.parse
import boto3
import base64
import io
from io import BytesIO
import requests
import os

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
styles = {1: {'name': 'Doctor', 'prompt': 'Woman, professional demeanor, doctor, hospital setting, medical equipment, Canon EOS R6, skilled photographer, Realistic, proportioned, Cinematic, medical expertise, caring pose, stethoscope in hands, empathetic, Hyper realistic.'}, 2: {'name': 'Nurse', 'prompt': 'Woman, nurturing expression, nurse, healthcare facility, scrubs, Nikon Z5, skilled photographer, Realistic, proportioned, Cinematic, compassionate care, comforting pose, medical tools in hands, attentive, Hyper realistic.'}, 3: {'name': 'Teacher', 'prompt': 'Woman, nurturing expression, teacher, classroom setting, educational materials, Sony A6400, skilled photographer, Realistic, proportioned, Cinematic, educational passion, teaching pose, books in hands, inspiring, Hyper realistic.'}, 4: {'name': 'Engineer', 'prompt': 'Woman, confident expression, engineer, engineering workspace, technical tools, Fujifilm X-T4, skilled photographer, Realistic, proportioned, Cinematic, engineering excellence, innovative pose, equipment in hands, determined, Hyper realistic.'}, 5: {'name': 'Lawyer', 'prompt': 'Woman, assertive expression, lawyer, courtroom setting, legal documents, Canon EOS 5D Mark III, skilled photographer, Realistic, proportioned, Cinematic, legal prowess, determined pose, briefcase in hands, focused, Hyper realistic.'}, 6: {'name': 'Accountant', 'prompt': 'Woman, analytical expression, accountant, office environment, financial documents, Panasonic Lumix GH5, skilled photographer, Realistic, proportioned, Cinematic, financial expertise, focused pose, calculator in hands, precise, Hyper realistic.'}, 7: {'name': 'Police Officer', 'prompt': 'Woman, determined expression, police officer, urban setting, uniform, night patrol, Nikon D750, skilled photographer, Realistic, proportioned, Cinematic, law enforcement, vigilant pose, equipment in hands, authoritative, Hyper realistic.'}, 8: {'name': 'Chef', 'prompt': "Woman, passionate expression, chef, kitchen setting, culinary tools, Canon EOS-1D X Mark III, skilled photographer, Realistic, proportioned, Cinematic, culinary mastery, creative pose, chef's knife in hands, inspired, Hyper realistic."}, 9: {'name': 'Pilot', 'prompt': 'Woman, confident expression, pilot, cockpit setting, aviation attire, Boeing 787 Dreamliner, skilled photographer, Realistic, proportioned, Cinematic, aviation expertise, cockpit pose, controls in hands, adventurous, Hyper realistic.'}, 10: {'name': 'Soldier', 'prompt': 'Woman, disciplined expression, soldier, military setting, camouflage uniform, M4 carbine, skilled photographer, Realistic, proportioned, Cinematic, military service, alert pose, rifle in hands, resilient, Hyper realistic.'}, 11: {'name': 'Software Developer', 'prompt': 'Woman, focused expression, software developer, coding environment, computer setup, MacBook Pro, skilled photographer, Realistic, proportioned, Cinematic, coding expertise, coding pose, laptop in hands, innovative, Hyper realistic.'}, 12: {'name': 'Secretary', 'prompt': 'Woman, organized expression, secretary, office setting, administrative tasks, Microsoft Surface Laptop, skilled photographer, Realistic, proportioned, Cinematic, administrative efficiency, multitasking pose, notepad in hands, efficient, Hyper realistic.'}, 13: {'name': 'Driver', 'prompt': 'Woman, focused expression, driver, steering wheel, car interior, Toyota Camry, skilled photographer, Realistic, proportioned, Cinematic, driving skill, confident pose, hands on the wheel, attentive, Hyper realistic.'}, 14: {'name': 'Salesperson', 'prompt': 'Woman, persuasive expression, salesperson, retail environment, product display, Sony Alpha 7C, skilled photographer, Realistic, proportioned, Cinematic, sales expertise, friendly pose, product in hands, persuasive, Hyper realistic.'}, 15: {'name': 'Electrician', 'prompt': 'Woman, skilled expression, electrician, electrical work environment, tools, Fluke Multimeter, skilled photographer, Realistic, proportioned, Cinematic, electrical expertise, inspecting pose, tools in hands, precise, Hyper realistic.'}, 16: {'name': 'Plumber', 'prompt': 'Woman, determined expression, plumber, plumbing workspace, tools, adjustable wrench, skilled photographer, Realistic, proportioned, Cinematic, plumbing proficiency, fixing pose, tools in hands, reliable, Hyper realistic.'}, 17: {'name': 'Mechanic', 'prompt': 'Woman, hands-on expression, mechanic, garage setting, tools, Snap-on wrench set, skilled photographer, Realistic, proportioned, Cinematic, automotive expertise, repairing pose, tools in hands, skilled, Hyper realistic.'}, 18: {'name': 'Construction Worker', 'prompt': 'Woman, sturdy expression, construction worker, construction site, safety gear, Caterpillar heavy equipment, skilled photographer, Realistic, proportioned, Cinematic, construction skills, lifting pose, tools in hands, resilient, Hyper realistic.'}, 19: {'name': 'Hairdresser', 'prompt': 'Woman, creative expression, hairdresser, salon setting, hair styling tools, Dyson Supersonic, skilled photographer, Realistic, proportioned, Cinematic, hairstyling artistry, styling pose, tools in hands, creative, Hyper realistic.'}, 20: {'name': 'Psychologist', 'prompt': 'Woman, empathetic expression, psychologist, therapy setting, counseling room, Psychology Today, skilled photographer, Realistic, proportioned, Cinematic, psychological expertise, listening pose, notepad in hands, empathetic, Hyper realistic.'}, 21: {'name': 'Journalist', 'prompt': 'Woman, inquisitive expression, journalist, newsroom setting, notepad and pen, Canon EOS-1D X Mark III, skilled photographer, Realistic, proportioned, Cinematic, journalistic passion, reporting pose, microphone in hands, curious, Hyper realistic.'}, 22: {'name': 'Graphic Designer', 'prompt': 'Woman, creative expression, graphic designer, design studio, Adobe Creative Cloud tools, Wacom Intuos, skilled photographer, Realistic, proportioned, Cinematic, design prowess, creating pose, graphic tablet in hands, imaginative, Hyper realistic.'}, 23: {'name': 'Farmer', 'prompt': 'Woman, hardworking expression, farmer, agricultural setting, farming tools, John Deere tractor, skilled photographer, Realistic, proportioned, Cinematic, farming expertise, planting pose, tools in hands, industrious, Hyper realistic.'}, 24: {'name': 'Mail Carrier', 'prompt': 'Woman, efficient expression, mail carrier, delivering mail, postal uniform, USPS vehicle, skilled photographer, Realistic, proportioned, Cinematic, mail delivery, walking pose, mailbag in hands, diligent, Hyper realistic.'}, 25: {'name': 'Receptionist', 'prompt': 'Woman, welcoming expression, receptionist, office lobby, front desk, iMac computer, skilled photographer, Realistic, proportioned, Cinematic, receptionist skills, greeting pose, phone in hands, hospitable, Hyper realistic.'}, 26: {'name': 'Waiter', 'prompt': 'Woman, attentive expression, waiter, restaurant setting, serving tray, elegant attire, skilled photographer, Realistic, proportioned, Cinematic, hospitality skills, serving pose, tray in hands, attentive, Hyper realistic.'}, 27: {'name': 'Accountant', 'prompt': 'Woman, analytical expression, accountant, financial office, analyzing documents, Panasonic Lumix GH5, skilled photographer, Realistic, proportioned, Cinematic, financial expertise, reviewing pose, calculator in hands, meticulous, Hyper realistic.'}, 28: {'name': 'Financial Analyst', 'prompt': 'Woman, analytical expression, financial analyst, data analysis, financial charts, Microsoft Excel, skilled photographer, Realistic, proportioned, Cinematic, financial analysis, analyzing pose, computer in hands, strategic, Hyper realistic.'}, 29: {'name': 'Project Manager', 'prompt': 'Woman, organized expression, project manager, project management workspace, Gantt chart, Apple MacBook Pro, skilled photographer, Realistic, proportioned, Cinematic, project management skills, planning pose, laptop in hands, strategic, Hyper realistic.'}, 30: {'name': 'Consultant', 'prompt': 'Woman, knowledgeable expression, consultant, consulting office, advising clients, ThinkPad laptop, skilled photographer, Realistic, proportioned, Cinematic, consulting expertise, advising pose, documents in hands, insightful, Hyper realistic.'}, 31: {'name': 'Nurse', 'prompt': 'Woman, caring expression, nurse, healthcare facility, scrubs, Sony A7 III, skilled photographer, Realistic, proportioned, Cinematic, compassionate care, comforting pose, medical tools in hands, attentive, Hyper realistic.'}, 32: {'name': 'Physical Therapist', 'prompt': 'Woman, empathetic expression, physical therapist, therapy room, rehabilitation equipment, Canon EOS 90D, skilled photographer, Realistic, proportioned, Cinematic, physical therapy, guiding pose, exercise tools in hands, supportive, Hyper realistic.'}, 33: {'name': 'Veterinarian', 'prompt': 'Woman, caring expression, veterinarian, veterinary clinic, treating animals, Nikon D5600, skilled photographer, Realistic, proportioned, Cinematic, veterinary care, caring pose, medical tools in hands, nurturing, Hyper realistic.'}, 34: {'name': 'Scientist/Researcher', 'prompt': 'Woman, curious expression, scientist/researcher, laboratory setting, scientific equipment, Leica Q2, skilled photographer, Realistic, proportioned, Cinematic, scientific exploration, researching pose, equipment in hands, analytical, Hyper realistic.'}, 35: {'name': 'Economist', 'prompt': 'Woman, analytical expression, economist, economic research, data analysis, Canon EOS-1D X Mark III, skilled photographer, Realistic, proportioned, Cinematic, economic expertise, analyzing pose, data in hands, strategic, Hyper realistic.'}, 36: {'name': 'Architect', 'prompt': 'Woman, visionary expression, architect, architectural workspace, design tools, Canon EOS R5, skilled photographer, Realistic, proportioned, Cinematic, architectural design, drawing pose, blueprint in hands, innovative, Hyper realistic.'}}
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
negative_prompt = 'helmet, armor, Watermark, Text, censored, deformed, bad anatomy, disfigured, poorly drawn face, mutated, extra limb, ugly, poorly drawn hands, missing limb, floating limbs, disconnected limbs, disconnected head, malformed hands, long neck, mutated hands and fingers, bad hands, missing fingers, cropped, worst quality, low quality, mutation, poorly drawn, huge calf, bad hands, fused hand, missing hand, disappearing arms, disappearing thigh, disappearing calf, disappearing legs, missing fingers, fused fingers, abnormal eye proportion, Abnormal hands, abnormal legs, abnormal feet,  abnormal fingers'

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



def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    # assumed_role_object=sts_client.assume_role(RoleArn="arn:aws:iam::479225850607:role/bedrock-crossaccount-role", RoleSessionName="LambdaRole")
    # credentials=assumed_role_object['Credentials']
    bedrock = boto3.client('bedrock-runtime')
    print("Assumed Role")
    s3_object = s3.get_object(Bucket=bucket, Key=key)
    file_byte_string = s3_object['Body'].read()
    photo_data = BytesIO(file_byte_string)
    style = styles[int(event['style'])]
    
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
    try:
        nuevaKey= "public/processed/"+style_name+"/" + (key.split('/'))[-1].replace(".png", ".jpeg")
        print(nuevaKey)
        # Upload image to s3
        s3.put_object(Bucket=bucket,
                     Key=nuevaKey,
                     Body=bin_data)
        publish_message(topic, "processed/"+style_name+"/" + (key.split('/'))[-1].replace(".png", ".jpeg")) 
        print("imagen generada guardada ! ")
    except Exception as e:
        print(e)
        print('Error putting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
        publish_message(topic,'ERROR')
        return {"ok" : "ok"}