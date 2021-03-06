from string import ascii_uppercase

from flask import Flask, request, render_template
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
import json
import openai
import sqlite3

import http.client

import os

DEEPGRAM_API_KEY = open('secret/deepgram_key').read().strip()
openai.api_key = open("secret/openai_key").read().strip()

app = Flask(__name__)

URL = "https://9272-188-39-25-218.ngrok.io/"

app.secret_key = os.urandom(12)
log = {}


@app.route("/data", methods=['GET'])
def database():
    """Return address database"""
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM data')
    return {a: {'address': b, 'capacity': c} for a, b, c in cur.fetchall()}


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming phone calls and ask for the address"""
    resp = VoiceResponse()
    number = request.values.get("From")
    log[number] = {'address': None, 'capacity': None}

    resp.say("Please enter your home number, street and city. Then press any key.", voice='alice')
    resp.record(action=URL + 'address/' + number,
                recordingStatusCallback=URL + "completed/address/" + number)

    return str(resp)


@app.route("/address/<number>", methods=['GET', 'POST'])
def address(number):
    """Continue after getting the address and ask for the number of people."""
    resp = VoiceResponse()
    resp.say("How many people are stranded there?", voice='alice')
    resp.record(action=URL + 'thanks',
                recordingStatusCallback=URL + "completed/capacity/" + number)

    return str(resp)


@app.route("/thanks", methods=['GET', 'POST'])
def thanks():
    """Say thanks after getting the information."""
    resp = VoiceResponse()
    resp.say("thanks", voice='alice')
    return str(resp)


@app.route("/completed/address/<number>", methods=['GET', 'POST'])
def address_completed(number):
    """Process the recorded response with the address."""
    print(request.values)
    url = request.values.get('RecordingUrl') + '.wav'
    print(url)
    process(url, number, 'address')
    return ''


@app.route("/completed/capacity/<number>", methods=['GET', 'POST'])
def capacity_completed(number):
    """Process the recorded response with the number of people."""
    print(request.values)
    url = request.values.get('RecordingUrl') + '.wav'
    print(url)
    process(url, number, 'capacity')
    commit_log(number)
    return ''


@app.route("/sms", methods=['GET', 'POST'])
def sms_survey():
    """Handle sms requests."""
    response = MessagingResponse()
    from_number = request.values.get('From')

    if from_number not in log.keys():
        response.message("Please enter your address.")
        log[from_number] = {'address': None, 'capacity': None}

    elif log[from_number]['address'] is None:
        log[from_number]['address'] = request.values.get('Body')
        response.message("How many people are stranded there?")

    elif log[from_number]['capacity'] is None:
        cap = request.values.get('Body')
        try:
            cap = int(cap)
            if cap <= 0:
                response.message("Please enter a valid number.\n\nHow many people are stranded there?")
            else:
                log[from_number]['capacity'] = cap
                commit_log(from_number)
                response.message(("Thank you for your response.\n\n"
                                  "Phone Number: {}\n"
                                  "Address: {}\n"
                                  "Number of People: {}").format(
                    from_number, data(from_number, 'address'), data(from_number, 'capacity')))
        except:
            response.message("Please enter a valid number.\n\nHow many people are stranded there?")

    else:
        response.message(("Thank you for your response.\n\n"
                          "Phone Number: {}\n"
                          "Address: {}\n"
                          "Number of People: {}").format(
            from_number, data(from_number, 'address'), data(from_number, 'capacity')))

    return str(response)


@app.route("/web", methods=['POST', 'GET'])
def web():
    """For testing. Handle web requests."""
    message = ''
    if request.method == 'POST':
        number = request.form.get('number')
        address = request.form.get('address')
        capacity = request.form.get('capacity')
        log[number] = {'address': address, 'capacity': capacity}
        commit_log(number)
        message = 'submitted'

    return render_template('webform.html', message=message)


@app.route("/test", methods=['POST', 'GET'])
def test():
    """Testing processing of a sample voice recording of an address."""
    url = 'https://api.twilio.com/2010-04-01/Accounts/ACcfef691231a0b455b289bdd859eefd71/Recordings' \
          '/RE0f8ab886b7428c8419e10fb000cd4b44' + '.wav '
    number = '1234'
    log[number] = {'address': None, 'capacity': None}
    process(url, number, 'address')
    return ''


def data(number, key):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT ' + key + ' FROM data WHERE number = ' + number)
    return cur.fetchall()[0]


def commit_log(number):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('INSERT INTO data VALUES (?, ?, ?)',
                (number, log[number]['address'], log[number]['capacity']))
    con.commit()
    log.pop(number)


def process(url, number, key):
    """Process an url with a voice recording of a [address,capacity] from the number."""
    conn = http.client.HTTPSConnection("api.deepgram.com")
    payload = '{\"url\":\"' + url + '\"}'
    headers = {
        'content-type': "application/json",
        'Authorization': "Token " + DEEPGRAM_API_KEY
    }
    keywords = '&'.join('keywords=' + l + ':2' for l in ascii_uppercase)
    conn.request("POST", "/v1/listen?numerals=true&" + keywords, payload, headers)

    res = conn.getresponse()
    transcript = json.loads(res.read().decode("utf-8"))['results']['channels'][0]['alternatives'][0]['transcript']
    print("raw: ", transcript)
    if key == 'address':
        transcript = openai.Completion.create(
            engine='text-davinci-001',
            prompt='the transcribed message is: "there is a flood at corn exchange take us from here"\n' +
                   'the mentioned address is: Corn Exchange, Cambridge\n' +
                   'the transcribed message is: churchill college c d. Street zero s\n' +
                   'the corrected address is: Churchill College, CB3 0DS\n' +
                   'the transcribed message is: ' + transcript
                   + '\nThe correct address is:',
            temperature=0.5,
            max_tokens=30,
            best_of=5,
            frequency_penalty=0,
            presence_penalty=0
        )["choices"][0]["text"].strip()
        print("after gpt: ", transcript)
    log[number][key] = transcript


if __name__ == "__main__":
    app.run(debug=True)
