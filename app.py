import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "karen123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_NUMBER_ID")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

@app.route("/")
def home():
    return "WhatsApp Bot LIVE"

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "fail", 403

@app.route("/webhook", methods=["POST"])
def receive():
    data = request.get_json()
    try:
        if data.get("object") == "whatsapp_business_account":
            msg_obj = data["entry"][0]["changes"][0]["value"]
            if "messages" in msg_obj:
                from_number = msg_obj["messages"][0]["from"]
                text = msg_obj["messages"][0]["text"]["body"]

                # AI answer
                ai_text = ask_groq(text)
                send_whatsapp(from_number, ai_text)
    except Exception as e:
        print(e)
    return "ok", 200

def ask_groq(prompt):
    if not groq_client:
        return "Bot not ready - missing GROQ key"
    r = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}]
    )
    return r.choices[0].message.content

def send_whatsapp(to, message):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type":"application/json"}
    payload = {"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":message}}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
