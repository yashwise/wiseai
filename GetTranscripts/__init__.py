import logging
import azure.functions as func
from helpers.helper import get_transcripts_from_container

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    blobs_list_names = get_transcripts_from_container()

    if blobs_list_names:
        return func.HttpResponse(blobs_list_names)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )