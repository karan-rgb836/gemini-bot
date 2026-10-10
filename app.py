from flask import Flask, request
import google.generativeai as genai
import requests

app = Flask(__name__)

# REPLACE THIS WITH YOUR GEMINI KEY FROM aistudio.google.com
GEMINI_KEY = "AQ.Ab8RN6LLUKBM9I4OlpeaGR3gVOaCvmbzCR2i5EST0rqL-IBhFQ"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """You are Gemini Code Builder, a WhatsApp helper that builds apps.
Give working code, short answers, file names first.
"""

@app.route("/")
def home():
    return "Gemini Bot is Running! Go to /webhook"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == "my_bot":
            return request.args.get("hub.challenge")
        return "Wrong token"

    data = request.get_json()
    try:
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' not in entry:
            return "OK", 200

        msg = entry['messages'][0]
        from_num = msg['from']
        text = msg['text']['body']

        print(f"User {from_num}: {text}")

        resp = model.generate_content(SYSTEM_PROMPT + "\nUser: " + text)
        reply_text = resp.text

        print(f"Gemini replied: {reply_text[:200]}")
        return "OK", 200

    except Exception as e:
        print(f"Error: {e}")
        return "OK", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)