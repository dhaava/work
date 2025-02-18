import os
from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# OpenAI API Key (stored in .env)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Twilio API Key details (stored in .env)
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# Initialize Twilio Client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Route to handle WhatsApp messages
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').lower()

    # Create Twilio response
    resp = MessagingResponse()
    msg = resp.message()

    # Check if the user asked for an Instagram caption
    if 'caption' in incoming_msg:
        user_input = incoming_msg.replace('caption', '').strip()  # Get text after 'caption'
        caption = generate_caption_from_openai(user_input)
        msg.body(f"Here's your caption: {caption}")
    else:
        msg.body("Send 'caption' followed by your request for an Instagram caption!")

    return str(resp)

# Function to generate Instagram caption using OpenAI GPT
def generate_caption_from_openai(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can change to "gpt-4" if needed
            messages=[
                {"role": "system", "content": "You are a creative Instagram caption generator."},
                {"role": "user", "content": f"Generate a catchy Instagram caption for: {text}"}
            ]
        )
        caption = response["choices"][0]["message"]["content"].strip()
        return caption
    except Exception as e:
        return "Error generating caption."

# Route to send WhatsApp message (optional)
@app.route('/send_whatsapp_message', methods=['POST'])
def send_whatsapp_message():
    to_number = request.json['to']
    message = request.json['message']
    send_whatsapp(to_number, message)
    return jsonify({"status": "Message sent"})

# Function to send WhatsApp messages using Twilio
def send_whatsapp(to, message):
    message = client.messages.create(
        body=message,
        from_='whatsapp:' + TWILIO_PHONE_NUMBER,
        to='whatsapp:' + to
    )
    return message.sid

if __name__ == '__main__':
    app.run(debug=True)
