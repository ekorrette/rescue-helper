from flask import Flask, request, render_template
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
import json
import openai

import http.client

import os

DEEPGRAM_API_KEY = open('secret/deepgram_key').read().strip()
openai.api_key = open("secret/openai_key").read().strip()

app = Flask(__name__)

URL = "https://9272-188-39-25-218.ngrok.io/"

app.secret_key = os.urandom(12)
log = {}
data = {
  "1": {
    "address": "1 Grange Road, CB3 9AS, Cambridge", 
    "capacity": "6"
  }, 
  "2": {
    "address": "3 Grange Road, CB3 9AS, Cambridge", 
    "capacity": "3"
  }, 
  "3": {
    "address": "Selwyn College, CB3 9DQ", 
    "capacity": "23"
  }
}


@app.route("/data", methods=['GET'])
def database():
    """Return address database"""
    return data


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming phone calls with a 'Hello world' message"""
    # Start our TwiML response
    resp = VoiceResponse()
    number = request.values.get("From")
    log[number] = {'address': None, 'capacity': None}

    # Read a message aloud to the caller
    resp.say("Please enter your home number, street and city. Then press any key.", voice='alice')
    resp.record(action=URL+'address/'+number,
            recordingStatusCallback=URL+"completed/address/"+number)

    return str(resp)


@app.route("/address/<number>", methods=['GET', 'POST'])
def address(number):
    resp = VoiceResponse()
    resp.say("How many people are stranded there?", voice='alice')
    resp.record(action=URL+'thanks',
            recordingStatusCallback=URL+"completed/capacity/"+number)

    return str(resp)


@app.route("/thanks", methods=['GET', 'POST'])
def thanks():
    resp = VoiceResponse()
    resp.say("thanks", voice='alice')
    return str(resp)


@app.route("/completed/address/<number>", methods=['GET', 'POST'])
def address_completed(number):
    print(request.values)
    url = request.values.get('RecordingUrl') + '.wav'
    print(url)
    process(url, number, 'address')
    return ''


@app.route("/completed/capacity/<number>", methods=['GET', 'POST'])
def capacity_completed(number):
    print(request.values)
    url = request.values.get('RecordingUrl') + '.wav'
    print(url)
    process(url, number, 'capacity')
    data[number] = log.pop(number)
    return ''


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
    url = 'https://api.twilio.com/2010-04-01/Accounts/ACcfef691231a0b455b289bdd859eefd71/Recordings/RE0f8ab886b7428c8419e10fb000cd4b44' + '.wav'
    number = '1234'
    log[number] = {'address': None, 'capacity': None}
    process(url, number, 'address')
    return ''


def process(url, number, key):
    conn = http.client.HTTPSConnection("api.deepgram.com")
    payload = '{\"url\":\"' + url + '\"}'
    headers = {
        'content-type': "application/json",
        'Authorization': "Token " + DEEPGRAM_API_KEY
    }
    conn.request("POST", "/v1/listen?numerals=true", payload, headers)

    res = conn.getresponse()
    transcript = json.loads(res.read().decode("utf-8"))['results']['channels'][0]['alternatives'][0]['transcript']
    print("raw: ", transcript)
    if key == 'address':
        transcript = openai.Completion.create(
            engine='text-davinci-001',
            prompt='This is an incorrect transcript of a UK address: \"' + transcript + '\"\nThe correct address with a corrected street name and matching post code is:',
            temperature=0.0,
            max_tokens=64,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )["choices"][0]["text"].strip()
        print("after gpt: ", transcript)
    log[number][key] = transcript


if __name__ == "__main__":
    app.run(debug=True)
