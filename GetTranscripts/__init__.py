import logging
import json
import azure.functions as func
from azure.storage.blob import BlobServiceClient

def read_from_container():
    # blob_access_key = ""
    blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=yashwiseteststore;AccountKey=mS1S0CHixET0Rb3u6LWsnNM1t6sx59Iyx0uNlgWwLc7deZawWIOh1Ym+aDKlTTCPhSON0BgRuZSB+AStzRz+5Q==;EndpointSuffix=core.windows.net")
    print("created the blob service client")
    # Get the container
    container_client = blob_service_client.get_container_client("yashwisetestcontainer")
    print("created the container client")
    # Get the blob
    blobs_list = list(container_client.list_blobs())
    blobs_list_names = list(map(lambda x: x.name, blobs_list))
    return blobs_list_names

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    blobs_list_names = read_from_container()

    if blobs_list_names:
        return func.HttpResponse(json.dumps({'blobs_list': blobs_list_names}) )
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )