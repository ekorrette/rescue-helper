from flask import Flask, request, session, url_for, redirect
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse

#from dotenv import load_dotenv
import os

app = Flask(__name__)

app.secret_key = os.urandom(12)

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

    if (from_number not in session.keys()):
        response.message("Please enter your address")
        session[from_number] = {'address': None, 'capacity': None}

    elif (session[from_number]['address'] is None):
        session[from_number]['address'] = request.values.get('Body')
        response.message("How many humanz please")
    elif (session[from_number]['capacity'] is None):
        session[from_number]['capacity'] = request.values.get('Body')
        response.message("Thank you for your response.")
    else:
        response.message("Address: {}\nCapacity: {}".format(session[from_number]['address'], session[from_number]['capacity']))

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
