import logging

import azure.functions as func
from helpers.helper import get_transcript_summary

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    transcript = req.params.get('transcript')
    regenerate = req.params.get('regenerate')
    # if not transcript:
    #     try:
    #         req_body = req.get_json()
    #     except ValueError:
    #         pass
    #     else:
    #         transcript = req_body.get('transcript')

    if transcript:
        response = get_transcript_summary(transcript, regenerate)
        return func.HttpResponse(response)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a transcript in the query string or in the request body for a personalized response.",
             status_code=200
        )




