import logging
import azure.functions as func
import requests
from simple_salesforce import Salesforce
import datetime

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

    req_body = req.get_json()
    logging.info(req_body)
    save_salesforce(req_body)
    
    return func.HttpResponse(
            "Saved to salesforce",
            status_code=200
    )

