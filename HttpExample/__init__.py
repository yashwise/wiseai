import logging

import azure.functions as func
import openai
from azure.storage.blob import BlobServiceClient


def read_from_container(file_name):
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


def summarise(file_content):
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


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    openai.api_key = "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"

    # text_file_content = read_from_container()

    # return_str = f"{text_file_content}. This HTTP triggered function executed successfully."

    # return func.HttpResponse(return_str)

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
        return_str += "-------\n"
        return_str += f"Here are the results: \n {summary}"
        return func.HttpResponse(return_str)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a transcript in the query string or in the request body for a personalized response.",
             status_code=200
        )




