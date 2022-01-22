from flask import Flask, request, url_for, redirect
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse

#from dotenv import load_dotenv
import os

app = Flask(__name__)

app.secret_key = os.urandom(12)
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
    resp.say("hello world!", voice='alice')

    return str(resp)

@app.route("/sms", methods=['GET', 'POST'])
def sms_survey():

    response = MessagingResponse()
    from_number = request.values.get('From')

    if (from_number not in data.keys()):
        response.message("Please enter your address.")
        data[from_number] = {'address': None, 'capacity': None}

    elif (data[from_number]['address'] is None):
        data[from_number]['address'] = request.values.get('Body')
        response.message("How many humanz please.")
        
    elif (data[from_number]['capacity'] is None):
        data[from_number]['capacity'] = request.values.get('Body')
        response.message("Thank you for your response.")
        
    else:
        response.message(("Address: {}\nCapacity: {}").format(data[from_number]['address'], data[from_number]['capacity']))

    return str(response)


if __name__ == "__main__":
    app.run(debug=True)
