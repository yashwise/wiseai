import logging
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # if blobs_list_names:
    return func.HttpResponse(
            "Saved to salesforce",
            status_code=200
    )

