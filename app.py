from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Fix CORS issue by allowing POST + OPTIONS + headers for Vercel frontend
CORS(app, resources={
    r"/chat": {
        "origins": ["https://bali2050-chatbot.vercel.app"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    
    if not user_input:
        return jsonify({"response": "Please enter a message."})
    
    if "bad lippspringe" not in user_input.lower():
        return jsonify({
            "response": "I'm designed to answer only about Bad Lippspringe. Please ask something related to that city."
        })

    prompt = (
        f"You are a helpful local guide for Bad Lippspringe, Germany. "
        f"Only answer questions related to Bad Lippspringe.\nUser: {user_input}\nGuide:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
