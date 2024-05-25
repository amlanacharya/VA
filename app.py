from flask import Flask, request, render_template
import subprocess
from gtts import gTTS
import wikipedia
import speech_recognition as sr
import webbrowser
import ecapture as ec
import pyjokes
import datetime
from twilio.rest import Client
import os
import requests
import playsound

app = Flask(__name__)


# Function to convert text to speech using gTTS
def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    playsound.playsound("response.mp3")


# Function to take voice input from the user (this will be modified for web input)
def take_command():
    return request.form.get('query').lower()


# Function to send messages using Twilio
def send_message(body, to):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(body=body, from_=os.getenv('TWILIO_NUMBER'), to=to)
    return message.sid


# Function to query Wolfram|Alpha Short Answers API
def query_wolframalpha(query):
    app_id = os.getenv('WOLFRAMALPHA_APP_ID')
    url = f"http://api.wolframalpha.com/v1/result?appid={app_id}&i={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "I couldn't find an answer to that question."


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    query = take_command()
    response = "I'm not sure how to help with that."

    if 'wikipedia' in query:
        response = 'Searching Wikipedia...'
        query = query.replace("wikipedia", "")
        results = wikipedia.summary(query, sentences=2)
        response = "According to Wikipedia: " + results

    elif 'open youtube' in query:
        youtube_url = "vnd.youtube://"
        response = f"<script>window.location.href='{youtube_url}';</script>"

    elif 'open google' in query:
        webbrowser.open("https://www.google.com")
        response = "Opening Google."

    elif 'search' in query:
        query = query.replace("search", "")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        response = f"Searching for {query}."

    elif 'time' in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        response = f"The time is {strTime}."

    elif 'date' in query:
        strDate = datetime.datetime.now().strftime("%Y-%m-%d")
        response = f"Today's date is {strDate}."

    elif 'send message' in query:
        response = "What should I say?"
        body = request.form.get('body')
        response = "To whom should I send the message?"
        to = request.form.get('to')
        message_sid = send_message(body, to)
        response = f"Message sent successfully with SID {message_sid}."

    elif 'take photo' in query:
        ec.capture(0, "Voice Assistant Camera", "img.jpg")
        response = "Taking a photo."

    elif 'joke' in query:
        joke = pyjokes.get_joke()
        response = joke

    elif 'calculate' in query:
        query = query.replace("calculate", "")
        answer = query_wolframalpha(query)
        response = f"The answer is {answer}."

    elif 'shutdown' in query:
        subprocess.call('shutdown /p /f')
        response = "Shutting down the system."

    elif 'exit' in query:
        response = "Goodbye!"

    speak(response)
    return render_template('index.html', response=response)


if __name__ == "__main__":
    app.run(debug=True)
