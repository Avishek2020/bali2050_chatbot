from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Initial system prompt (only once per session)
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a helpful assistant focused only on Bad Lippspringe, Germany. "
        "You only provide information related to the city (services, weather, history, transport, events, etc.). "
        "If a query is unrelated, politely say: "
        "'I'm here to help with information about Bad Lippspringe. Could you ask something related to the city?'"
    )
}

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return '', 204

    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"response": "Please enter a message."})

    # Use Flask session to persist conversation context
    if "history" not in session:
        session["history"] = [SYSTEM_PROMPT]

    session["history"].append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session["history"],
            max_tokens=1000
        )
        reply = response.choices[0].message.content.strip()

        # Add assistant response to history
        session["history"].append({"role": "assistant", "content": reply})
        session.modified = True

        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
