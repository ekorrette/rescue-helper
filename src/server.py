from flask import Flask, request, url_for, redirect
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse

#from dotenv import load_dotenv
import os

app = Flask(__name__)

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
    resp.say("hello world!", voice='alice')

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

if __name__ == "__main__":
    app.run(debug=True)
