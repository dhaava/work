import os
from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import google.generativeai as genai
import logging
from twilio.base.exceptions import TwilioRestException

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Environment Variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')

# Initialize Twilio Client
twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/')
def home():
    return "Flask app is running on Render!"

# ✅ Handle incoming WhatsApp messages
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').lower()
    sender_number = request.values.get('From')  

    print(f"📩 Incoming message from {sender_number}: {incoming_msg}")  

    if 'caption' in incoming_msg:
        user_input = incoming_msg.replace('caption', '').strip()
        response_text = generate_content(user_input, "caption")
        message_sids = send_long_message(sender_number, f"📸 *Instagram Caption:* {response_text}")

    elif 'script' in incoming_msg:
        user_input = incoming_msg.replace('script', '').strip()
        response_text = generate_content(user_input, "script")
        message_sids = send_long_message(sender_number, f"🎬 *Instagram Script:* {response_text}")

    else:
        message_sids = send_long_message(sender_number, "Send *'caption'* or *'script'* followed by your topic to get Instagram content!")

    return jsonify({"status": "Message processed", "message_sids": message_sids})

# ✅ Function to send long messages with error handling
def send_long_message(to, message):
    max_length = 1600  # Twilio limit per message
    parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]  

    message_sids = []
    for part in parts:
        try:
            msg = twilio_client.messages.create(
                body=part,
                from_=TWILIO_PHONE_NUMBER,
                to='whatsapp:' + to
            )
            message_sids.append(msg.sid)
        except TwilioRestException as e:
            logging.error(f"⚠️ Twilio Error: {e.msg}")
            return [f"⚠️ Twilio Error: {e.msg}"]

    return message_sids  # ✅ Return message SIDs for tracking

# ✅ Generate Instagram content using Gemini AI
def generate_content(text, content_type):
    try:
        prompt = f"Generate an engaging Instagram {content_type} for: {text}"

        # ✅ Gemini API call with error handling
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        if not response or not response.candidates:
            logging.warning(f"⚠️ No response from Gemini for: {text}")
            return "⚠️ No response generated. Try again later."

        content_parts = response.candidates[0].content.parts if response.candidates[0].content else []
        generated_text = content_parts[0].text if content_parts else "⚠️ No valid content generated."

        # ✅ Trim to 1600 characters to avoid Twilio error 21617
        trimmed_text = generated_text[:1600]

        logging.debug(f"Generated {content_type}: {trimmed_text}")
        return trimmed_text

    except Exception as e:
        logging.error(f"Error generating {content_type}: {str(e)}")
        return f"⚠️ Error generating {content_type}. Please try again later."

# ✅ API to send manual WhatsApp messages
@app.route('/send_whatsapp_message', methods=['POST'])
def send_whatsapp_message():
    """API Endpoint to send a WhatsApp message via Twilio"""
    try:
        data = request.get_json()
        if not data or 'to' not in data or 'message' not in data:
            return jsonify({"error": "Missing 'to' or 'message' field"}), 400

        to_number = data['to']
        message = data['message']

        # ✅ Send WhatsApp message
        message_sids = send_whatsapp(to_number, message)

        return jsonify({
            "status": "Message sent",
            "message_sids": message_sids
        })

    except Exception as e:
        logging.error(f"Error in send_whatsapp_message: {str(e)}")
        return jsonify({"error": f"Failed to send message: {str(e)}"}), 500

# ✅ Function to send manual WhatsApp messages with tracking
def send_whatsapp(to, message):
    max_length = 1600  
    parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]  

    message_sids = []
    for part in parts:
        try:
            msg = twilio_client.messages.create(
                body=part,
                from_=TWILIO_PHONE_NUMBER,
                to='whatsapp:' + to
            )
            message_sids.append(msg.sid)
        except TwilioRestException as e:
            logging.error(f"⚠️ Twilio Error: {e.msg}")
            return [f"⚠️ Twilio Error: {e.msg}"]

    return message_sids  

if __name__ == '__main__':
    app.run(debug=True)
