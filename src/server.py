from flask import Flask, request, url_for, redirect, render_template
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
from deepgram import Deepgram
import json, requests, asyncio

import http.client

#from dotenv import load_dotenv
import os

DEEPGRAM_API_KEY = open('../secret/deepgram_key').read().strip()

app = Flask(__name__)

URL = "http://9272-188-39-25-218.ngrok.io/"

app.secret_key = os.urandom(12)
log = {}
data = {}

@app.route("/data", methods=['GET'])
def database():
    """Return address database"""
    return data


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming phone calls with a 'Hello world' message"""
    # Start our TwiML response
    resp = VoiceResponse()

    # Read a message aloud to the caller
    resp.say("hello world! say the stuff and press a key.", voice='alice')
    resp.record(action=URL+'thanks',
            recordingStatusCallback=URL+"completed")

    return str(resp)

@app.route("/thanks", methods=['GET', 'POST'])
def thanks():
    resp = VoiceResponse()
    resp.say("thanks", voice='alice')
    return str(resp)


@app.route("/completed", methods=['GET', 'POST'])
def record_completed():
    print(request.values)
    url = request.values.get('RecordingUrl') + '.wav'
    print(url)
    process(url)

    resp = VoiceResponse()
    resp.say("your response has been processed", voice='alice')
    return str(resp)


@app.route("/sms", methods=['GET', 'POST'])
def sms_survey():
    response = MessagingResponse()
    from_number = request.values.get('From')

    if (from_number not in log.keys()):
        response.message("Please enter your address.")
        log[from_number] = {'address': None, 'capacity': None}

    elif (log[from_number]['address'] is None):
        log[from_number]['address'] = request.values.get('Body')
        response.message("How many people are stranded there?")

    elif (log[from_number]['capacity'] is None):
        cap = request.values.get('Body')
        try:
            cap = int(cap)
            if (cap <= 0):
                response.message("Please enter a valid number.\n\nHow many people are stranded there?")
            else:
                log[from_number]['capacity'] = cap
                data[from_number] = log.pop(from_number)
        except:
            response.message("Please enter a valid number.\n\nHow many people are stranded there?")

    else:
        response.message(("Thank you for your response.\n\n"
                          "Phone Number: {}\n"
                          "Address: {}\n"
                          "Number of People: {}").format(
            from_number, data[from_number]['address'], data[from_number]['capacity']))

    return str(response)


@app.route("/web", methods=['POST', 'GET'])
def web():
    message = ''
    if request.method == 'POST':
        number = request.form.get('number')  # access the data inside 
        address = request.form.get('address')
        capacity = request.form.get('capacity')
        data[number] = {'address': address, 'capacity': capacity}
        message = 'submitted'

    return render_template('webform.html', message=message)

@app.route("/test", methods=['POST', 'GET'])
def test():
    url = 'https://api.twilio.com/2010-04-01/Accounts/ACcfef691231a0b455b289bdd859eefd71/Recordings/RE50532561317f075f7e0c33c69d68ca4b' + '.wav'
    process(url)
    return ''

def process(url):
    conn = http.client.HTTPSConnection("api.deepgram.com")
    payload = '{\"url\":\"' + url + '\"}'
    headers = {
        'content-type': "application/json",
        'Authorization': "Token " + DEEPGRAM_API_KEY
    }
    print(payload)
    conn.request("POST", "/v1/listen", payload, headers)

    res = conn.getresponse()
    data = res.read()
    transcript = json.loads(data.decode("utf-8"))['results']['channels'][0]['alternatives'][0]['transcript']
    print(transcript)



if __name__ == "__main__":
    app.run(debug=True)
