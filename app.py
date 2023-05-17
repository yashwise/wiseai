# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from tkinter.messagebox import RETRY
from flask import Flask, request
from flask_cors import CORS
from helpers.helper import *
import json
# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)
CORS(app)
# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World'

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/getdeals')
# ‘/’ URL is bound with hello_world() function.
def getdeals():
    return get_deal_list_from_cosmos_container()
    


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/gettranscripts')
# ‘/’ URL is bound with hello_world() function.
def getTranscripts():
    blobs_list_names = get_transcript_list_from_blob_container()
    return blobs_list_names

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/transcriptsummary')
# ‘/’ URL is bound with hello_world() function.
def transcriptSummary():
    response = get_transcript_summary(request.args.get('transcript'), request.args.get('regenerate'))
    return response
 
# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/savespiced', methods = ['POST'])
# ‘/’ URL is bound with hello_world() function.
def savespiced():
    print("REQUEST", request.json)
    transcript_name = request.json['transcript_name']
    read_write_transcript_info_from_cosmos(transcript_name, request.json)
    return ("ok")


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/getdeal')
# ‘/’ URL is bound with hello_world() function.
def getdeal():
    return read_write_deal_info_from_cosmos(request.args.get('deal_name'))
    
# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/savedealsummary', methods = ['POST'])
# ‘/’ URL is bound with hello_world() function.
def savedealsummary():
    print("REQUEST", request.json)
    deal_name = request.json['deal_name']
    read_write_deal_info_from_cosmos(deal_name, request.json)
    return ("ok")

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/getdealsummary')
# ‘/’ URL is bound with hello_world() function.
def getdealsummary():
    return generate_deal_summary(request.args.get('deal_name'))


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/sendaudio', methods = ['POST'])
# ‘/’ URL is bound with hello_world() function.
def getaudio():
    print("reaching1 here")
    print(request.files)
    print(request.files['data'])
    # write_audio(request.files['data'])
    print("in write audio")

    # # print("writing to container")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # webm_filename = f"webm_{timestamp}.webm"
    transcript_filename = f"transcript_{timestamp}.txt"
    # blob_container_client = get_blob_container_client(BLOB_CONTAINER_NAME_AUDIO)
    # blob_container_client.upload_blob(webm_filename, request.files['data'])
    # # print("written to container")
    sound = AudioSegment.from_file(request.files['data'],"webm")
    # # write webm file
    print("loaded from webm to wav")
    AUDIO_FILE = "transcript.wav"
    sound.export(AUDIO_FILE, format="wav")
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file
        transcription = r.recognize_google(audio)
        print("Transcription: " + transcription)
        write_transcript(transcription, transcript_filename)
    return("ok")




# main driver function
if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()