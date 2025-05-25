from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    if "bad lippspringe" not in user_input.lower():
        return jsonify({"response": "I'm designed to answer only about Bad Lippspringe. Please ask something related to that city."})

    prompt = f"You are a helpful local guide for Bad Lippspringe, Germany. Only answer questions related to Bad Lippspringe.\nUser: {user_input}\nGuide:"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    reply = response['choices'][0]['message']['content']
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(port=5000)
