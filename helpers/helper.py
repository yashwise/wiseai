
from cmath import log
from azure.storage.blob import BlobServiceClient, ContentSettings
import json
import openai
import os
from azure.cosmos import CosmosClient, PartitionKey
from pydub import AudioSegment
import speech_recognition as sr
import datetime

openai.api_key = "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"
REMOTE_BLOB_CONN_STR = "DefaultEndpointsProtocol=https;AccountName=yashwiseteststore;AccountKey=mS1S0CHixET0Rb3u6LWsnNM1t6sx59Iyx0uNlgWwLc7deZawWIOh1Ym+aDKlTTCPhSON0BgRuZSB+AStzRz+5Q==;EndpointSuffix=core.windows.net"
LOCAL_BLOB_CONN_STR = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
BLOB_CONTAINER_NAME_TRANSCRIPT = "yashwisetestcontainer"
BLOB_CONTAINER_NAME_AUDIO = "yashwisetestaudio"
COSMOS_ENDPOINT = "https://yashwisecosmos.documents.azure.com:443/"
COSMOS_KEY = "iX4V0kcpnBpCwHRIaAREG03RNO6YqAIa4gqh3EjZUvToJ5qrOGGrcGkKh7jjUqRbVC7b1ujHgocfACDb31arWw=="
COSMOS_DATABASE_NAME = "yashwise"
TRANSCRIPT_CONTAINER_NAME = "transcript_summaries"
DEAL_CONTAINER_NAME = "deal_summaries"

def get_blob_container_client(container_name):
    print(f"Getting Blob Container client for {container_name}")
    blob_service_client = BlobServiceClient.from_connection_string(LOCAL_BLOB_CONN_STR)
    blob_container_client = blob_service_client.get_container_client(container_name)
    return blob_container_client

def get_transcript_list_from_blob_container():
    print("Getting List of transcripts from Blob Container client")
    blob_container_client = get_blob_container_client()
    blobs_list = list(blob_container_client.list_blobs())
    blobs_list_names = list(map(lambda x: x.name, blobs_list))
    response = json.dumps({'blobs_list': blobs_list_names}) 
    return response

def get_transcript_content_from_blob_container(file_name: str):
    print(f"Getting Transcript content for {file_name}")
    container_client = get_blob_container_client()
    blob_client = container_client.get_blob_client(file_name)
    blob_content = blob_client.download_blob().content_as_text()
    return blob_content

def get_cosmos_container_client(container_name):
    print(f"Getting Cosmos Container Client for {container_name}")
    cosmos_client = CosmosClient(url=COSMOS_ENDPOINT, credential=COSMOS_KEY)
    db_client = cosmos_client.get_database_client(COSMOS_DATABASE_NAME)
    container_client = db_client.get_container_client(container_name)
    return container_client

def get_deal_list_from_cosmos_container():
    print(f"Getting deal list from cosmos")
    deal_container_client = get_cosmos_container_client(DEAL_CONTAINER_NAME)
    query = 'SELECT * FROM c'
    deals = list(deal_container_client.query_items(query, enable_cross_partition_query=True))
    response = json.dumps({'deals': deals})
    print(f"Returning {response}")
    return response

def read_write_transcript_info_from_cosmos(transcript_name: str, transcript_info: dict = {}):
    transcript_container_client = get_cosmos_container_client(TRANSCRIPT_CONTAINER_NAME)
    try:
        print(f"Trying to read transcript info for {transcript_name}")
        result = transcript_container_client.read_item(item=transcript_name, partition_key=transcript_name)
        if result and not transcript_info: # READ
            print(f"Found info for {transcript_name} AND no info given. Returning entry")
            return result 
        if result and transcript_info: # UPDATE
            print(f"Found info for {transcript_name} AND info given. Updating entry")
            result.update(transcript_info)
            transcript_container_client.upsert_item(result)
        return result
    except: # empty result
        if not transcript_info:
            print(f"Did not find any info for {transcript_name} AND no info given. Returning empty result")
            return {}
        if transcript_info:  # CREATE
            print(f"Did not find any info for {transcript_name} BUT info given. Creating entry")
            transcript_info['id'] = transcript_info['transcript_name']
            transcript_container_client.create_item(transcript_info)

def get_transcript_summary(transcript_name: str, regenerate: bool = False):
    
    transcript_info = read_write_transcript_info_from_cosmos(transcript_name)
    transcript_content = get_transcript_content_from_blob_container(transcript_name)

    questions = []
    questions.append( ["summary","What is the summary of the meeting?"])
    questions.append( ["pain","What are the pain points of the customer?"])
    questions.append( ["impact","What is the business impact ?"])
    questions.append( ["critical_event","What are the critical events for the customer?"])
    questions.append( ["decision_criteria","What is the decision criteria mentioned bny the customer?"])

    if len(transcript_info):
        print(f"transcript info already exists for {transcript_name}")
        result = { k: transcript_info[k] for k in [i[0] for i in questions] }
    else:
        print(f"transcript info does not exists for {transcript_name}")
        print(f"querying open ai")
        result = {}
        for [category,question] in questions:
            prompt = f"You are a meeting summarizer and you are expected to answer questions we ask you about the meeting."
            prompt += f"In the meeting notes we just shared below \"{question}\"\n"
            prompt += f"{transcript_content}"
            completions = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=500,
                n=1
            )
            message = completions.choices[0].text.strip()
            split_message = message.split(".\"\n")
            if len(split_message) == 2:
                message = split_message[1]
            result[category] = message
    
    result['transcript_name'] = transcript_name
    
    response = json.dumps({ 
        'transcript_content': transcript_content, 
        'spiced': result
    }) 
    return response

def read_write_deal_info_from_cosmos(deal_name: str, deal_info: dict = {}):
    deal_container_client = get_cosmos_container_client(DEAL_CONTAINER_NAME)
    try:
        print(f"Trying to read deal info for {deal_name}")
        result = deal_container_client.read_item(item=deal_name, partition_key=deal_name)
        if result and not deal_info:
            print(f"Found info for {deal_name} AND no info given. Returning entry")
            response = { k: result[k] for k in ['id', 'company_name','transcript_list','deal_name','summary'] if k in result }
            return json.dumps({'deal_data': response})
        if result and deal_info:
            print(f"Found info for {deal_name} AND info given. Updating entry")
            result.update(deal_info)
            deal_container_client.upsert_item(deal_info)
    except: # empty result
        if not deal_info:
            print(f"Did not find any info for {deal_name} AND no info given. Returning empty result")
            return {}
        if deal_info:
            print(f"Did not find any info for {deal_name} BUT info given. Creating entry")
            deal_info['id'] = deal_info['deal_name']
            deal_container_client.create_item(deal_info)

def generate_deal_summary(deal_name: str):
    print(f"Trying to read deal info for {deal_name}")
    deal_container_client = get_cosmos_container_client(DEAL_CONTAINER_NAME)
    result = deal_container_client.read_item(item=deal_name, partition_key=deal_name)
    transcript_list = result['transcript_list']
    if len(transcript_list) == 1:
        transcript_summary = get_transcript_summary(transcript_list[0])
        return json.dumps({'deal_summary': json.loads(transcript_summary)['spiced']['summary']})
    else:
        print(f"User requested new deal summary. Querying openai")
        prompt = f"You are a deal summariser. Each deal consists of multiple meetings."
        prompt += f"And each meeting has its own summary."
        prompt += f"I want you to generate the summary of the deal based on the meeting summaries I have shared below.\n"
        for i, transcript in enumerate(transcript_list):
            transcript_summary = get_transcript_summary(transcript)
            transcript_summary = json.loads(transcript_summary)['spiced']['summary']
            prompt += f"Summary of Meeting {i+1}: {transcript_summary} \n"
            completions = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=500,
                n=1
            )
            message = completions.choices[0].text.strip()
        return json.dumps({'deal_summary': message})


def write_audio(file):
    print("in write audio")

    print("writing to container")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    webm_filename = f"webm_{timestamp}.webm"
    transcript_filename = f"transcript_{timestamp}.txt"
    blob_container_client = get_blob_container_client(BLOB_CONTAINER_NAME_AUDIO)
    blob_container_client.upload_blob(webm_filename, file)
    print("written to container")
    sound = AudioSegment.from_file(file,"webm")
    # write webm file
    print("loaded from webm to wav")
    AUDIO_FILE = "transcript.wav"
    sound.export(AUDIO_FILE, format="wav")
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file
        transcription = r.recognize_google(audio)
        print("Transcription: " + transcription)
        write_transcript(transcription, transcript_filename)
        
def write_transcript(transcript, transcript_filename):
    print("in write transcript")
    blob_container_client = get_blob_container_client(BLOB_CONTAINER_NAME_TRANSCRIPT)
    blob_container_client.upload_blob(transcript_filename, transcript, content_settings=ContentSettings(content_type='text/plain'))
    print("wrote transcript")

"""
do upload transcript to deal
"""