import logging

import azure.functions as func
import openai
from azure.storage.blob import BlobServiceClient
import requests
import json
from simple_salesforce import Salesforce
import datetime

def read_from_container(file_name: str):
    # blob_access_key = ""
    blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=yashwiseteststore;AccountKey=mS1S0CHixET0Rb3u6LWsnNM1t6sx59Iyx0uNlgWwLc7deZawWIOh1Ym+aDKlTTCPhSON0BgRuZSB+AStzRz+5Q==;EndpointSuffix=core.windows.net")
    print("created the blob service client")
    # Get the container
    container_client = blob_service_client.get_container_client("yashwisetestcontainer")
    print("created the container client")
    # Get the blob
    blob_client = container_client.get_blob_client(file_name)
    print("created the blob client")
    # Download the blob content to a string
    blob_content = blob_client.download_blob().content_as_text()
    # Print the content
    print(blob_content)
    return blob_content


def summarise(file_content: str):
    openai.api_key = "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"
    questions = []
    questions.append( "What is the summary of the meeting?")
    questions.append( "What are the pain points of the customer?")
#     questions.append( "What is the business impact ?")
    questions.append( "What are the critical events for the customer?")
    questions.append( "What is the decision criteria mentioned by the customer?")

    result_str = ''
    # for category in ["Situation", "Pain point", "Decision criteria"]:
    for question in questions:
        # prompt = f"summarise the {category} from the following text. {file_content}"
        prompt = f"You are a meeting summarizer and you are expected to answer questions we ask you about the meeting."
        prompt += f"In the meeting notes we just shared below \"{question}\"\n"
        prompt += f"{file_content}"
#         print(prompt)
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
        to_add = f"{question}\n{message}"
#         print(to_add)
        result_str = result_str + "\n" + to_add
    return result_str


def authenticate_salesforce():
    print("Authenticating salesforce")
    client_id = "3MVG9n_HvETGhr3AUbUhMJxrsZMZ1ps2sRIi7PE33If0IPT0cMGGhSHHNqGiD5SIi7QtqioXJsalKj5FDV1e_", # Consumer Key
    client_secret = "18564E10B97B81B5B1B06E1B112FCA051B29686E022F0B0F3F4BB81E54EEA569", # Consumer Secret
    username = "shravani.vatti@gmail.com", # The email you use to login
    password = "Ardizen!2019ZW5Ho5vTJ5wMaS4xV1cJVdH6" # Concat your password and your security token

    params = {
            "grant_type": "password",
            "client_id": client_id, # Consumer Key
            "client_secret": client_secret,  # Consumer Secret
            "username": username, # The email you use to login
            "password": password # Concat your password and your security token
        }
   
    r = requests.post("https://login.salesforce.com/services/oauth2/token", params=params)
        
    access_token = r.json().get("access_token")
    instance_url = r.json().get("instance_url")

    instance_data = {
        "access_token": access_token,
        "instance_url": instance_url
    }

    return instance_data

def save_salesforce(return_str: str):
    instance_data = authenticate_salesforce()
    sf = Salesforce(instance_url=instance_data[ "instance_url"], session_id=instance_data["access_token"])
    print("Getting contact")
    contact = sf.Contact.get_by_custom_id('email', 'abhisekupadhyaya@example.com')
    today = datetime.date.today()
    call = {
        'Subject': 'SPICED Meeting',
        'WhoId': contact["Id"], # Replace with the ID of the contact you want to associate the call with
        'ActivityDate': str(today),
        'Description': return_str,
        'Status': 'Completed'
    }
    print("Saving call")
    sf.Task.create(call)
    print("Saved call")
    return

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    transcript = req.params.get('transcript')
    if not transcript:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            transcript = req_body.get('transcript')

    if transcript:
        transcript_content = read_from_container(transcript)
        summary = summarise(transcript_content)
        print(summary)
        return_str = f"Here is the transcript: \n{transcript_content} "
        return_str += "\n\n\n-------\n\n\n"
        return_str += f"Here are the results: \n {summary}"

        # save in salesforce
        save_salesforce(return_str)

        return func.HttpResponse(return_str)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a transcript in the query string or in the request body for a personalized response.",
             status_code=200
        )




