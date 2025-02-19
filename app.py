import os
from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Gemini API Key (stored in .env)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Twilio API Key details (stored in .env)
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# Initialize Twilio Client
twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/')
def home():
    return "Flask app is running on Render!"

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
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # ✅ Set API key

def generate_content(text, content_type):
    try:
        prompt = f"Generate an engaging Instagram {content_type} for: {text}"

        response = genai.generate_text(
            model="models/gemini-1.5-flash",
            prompt=prompt
        )

        generated_text = response.result.strip()

        # ✅ Trim to 1600 characters (to avoid Twilio error 21617)
        trimmed_text = generated_text[:1600]

        logging.debug(f"Generated {content_type}: {trimmed_text}")
        return trimmed_text

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
