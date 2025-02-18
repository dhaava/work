from flask import Flask, request, jsonify
from twilio.rest import Client
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# DeepAI API Key (replace with your actual API key)
DEEPAI_API_KEY = 'd6fdc560-7f68-425f-9023-7369fc67138a'

# Twilio API Key details
TWILIO_PHONE_NUMBER = '+918848974677'
ACCOUNT_SID = 'AC08d35fcf128bd15030db3cf518f3e28a'
AUTH_TOKEN = '3013436188ab408262e917c5c920ebae'
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
        user_input = incoming_msg.replace('caption', '').strip()  # Get text after the keyword 'caption'
        caption = generate_caption_from_deepai(user_input)
        msg.body(f"Here's your caption: {caption}")
    else:
        msg.body("Send 'caption' followed by your request for an Instagram caption!")

    return str(resp)

# Function to generate Instagram caption using DeepAI
def generate_caption_from_deepai(text):
    url = "https://api.deepai.org/api/text-generator"
    response = requests.post(
        url,
        data={'text': text},
        headers={'api-key': DEEPAI_API_KEY}
    )
    caption = response.json().get('output', 'Sorry, unable to generate caption.')
    return caption

# Route to handle WhatsApp message sending (optional)
@app.route('/send_whatsapp_message', methods=['POST'])
def send_whatsapp_message():
    to_number = request.json['to']
    message = request.json['message']
    send_whatsapp(to_number, message)
    return jsonify({"status": "Message sent"})

# Function to send messages via WhatsApp using Twilio
def send_whatsapp(to, message):
    message = client.messages.create(
        body=message,
        from_='whatsapp:' + TWILIO_PHONE_NUMBER,
        to='whatsapp:' + to
    )
    return message.sid

if __name__ == '__main__':
    app.run(debug=True)
