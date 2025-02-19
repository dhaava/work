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

# Twilio API Key details (stored in .env)
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# Initialize Twilio Client
twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Route to handle WhatsApp messages
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').lower()

    # Create Twilio response
    resp = MessagingResponse()
    msg = resp.message()

    if 'caption' in incoming_msg:
        user_input = incoming_msg.replace('caption', '').strip()
        response_text = generate_content(user_input, "caption")
        msg.body(f"📸 *Instagram Caption:* {response_text}")

    elif 'script' in incoming_msg:
        user_input = incoming_msg.replace('script', '').strip()
        response_text = generate_content(user_input, "script")
        msg.body(f"🎬 *Instagram Script:* {response_text}")

    else:
        msg.body("Send *'caption'* or *'script'* followed by your topic to get Instagram content!")

    return str(resp)

# Function to generate Instagram content (captions/scripts)
import logging
logging.basicConfig(level=logging.DEBUG)

def generate_content(text, content_type):
    try:
        openai.api_key = OPENAI_API_KEY  
        prompt = f"Generate an engaging Instagram {content_type} for: {text}"
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Instagram content creator."},
                {"role": "user", "content": prompt}
            ]
        )

        generated_text = response["choices"][0]["message"]["content"].strip()
        logging.debug(f"Generated {content_type}: {generated_text}")
        return generated_text

    except Exception as e:
        logging.error(f"Error generating {content_type}: {str(e)}")
        return f"⚠️ Error generating {content_type}. Please try again later."

# Route to send WhatsApp message (optional)
@app.route('/send_whatsapp_message', methods=['POST'])
def send_whatsapp_message():
    to_number = request.json['to']
    message = request.json['message']
    send_whatsapp(to_number, message)
    return jsonify({"status": "Message sent"})

# Function to send WhatsApp messages using Twilio
def send_whatsapp(to, message):
    message = twilio_client.messages.create(
        body=message,
        from_='whatsapp:' + TWILIO_PHONE_NUMBER,
        to='whatsapp:' + to
    )
    return message.sid

if __name__ == '__main__':
    app.run(debug=True)
