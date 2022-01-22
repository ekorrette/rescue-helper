from flask import Flask, request, session, url_for, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_survey():
    response = MessagingResponse()
    from_number = request.values.get('From')

    if (from_number not in session.keys()):
        response.message("Please enter your address.")
        session[from_number] = {'address': None, 'capacity': None}

    elif (session[from_number]['address'] is None):
        session[from_number]['address'] = request.values.get('Body')
        response.message("How many humanz please.")
        print(session)
        
    elif (session[from_number]['capacity'] is None):
        session[from_number]['capacity'] = request.values.get('Body')
        response.message("Thank you for your response.")
        
    else:
        response.message(("Address: {}\nCapacity: {}").format(session[from_number]['address'], session[from_number]['capacity']))

    return str(response)
