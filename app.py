from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app, supports_credentials=True)

# One-time system prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a helpful assistant that only answers questions related to Bad Lippspringe, Germany — including local services, weather, events, transportation, history, and places of interest.\n"
        "If a user asks something unrelated (like about other cities or global topics), DO NOT answer it.\n"
        "Instead, respond with a polite fallback message in the same language as the user's query, based on the following translations:\n"
        "- English: I'm really sorry, but I'm designed to assist only with information about Bad Lippspringe. Could you please check your question and ask again about something related to Bad Lippspringe? I'd be happy to help you!\n"
        "- German: Es tut mir leid, aber ich bin darauf spezialisiert, nur Informationen über Bad Lippspringe bereitzustellen. Könntest du bitte deine Frage überprüfen und erneut etwas zu Bad Lippspringe fragen? Ich helfe dir gerne weiter!\n"
        "- Portuguese: Desculpe, mas fui projetado para fornecer informações apenas sobre Bad Lippspringe. Poderia verificar sua pergunta e perguntar novamente algo relacionado a Bad Lippspringe? Ficarei feliz em ajudar!\n"
        "- Spanish: Lo siento mucho, pero estoy diseñado para proporcionar información solo sobre Bad Lippspringe. ¿Podrías revisar tu pregunta y volver a preguntar algo relacionado con Bad Lippspringe? ¡Estaré encantado de ayudarte!\n"
        "- Turkish: Üzgünüm, ancak yalnızca Bad Lippspringe hakkında bilgi sağlamak üzere tasarlandım. Lütfen sorunuzu kontrol edip Bad Lippspringe ile ilgili bir şey sorar mısınız? Size yardımcı olmaktan memnuniyet duyarım!\n"
    )
}

# Fallback messages by language
FALLBACK_MESSAGES = {
    "en": "I'm really sorry, but I'm designed to assist only with information about Bad Lippspringe. Could you please check your question and ask again about something related to Bad Lippspringe? I'd be happy to help you!",
    "de": "Es tut mir leid, aber ich bin darauf spezialisiert, nur Informationen über Bad Lippspringe bereitzustellen. Könntest du bitte deine Frage überprüfen und erneut etwas zu Bad Lippspringe fragen? Ich helfe dir gerne weiter!",
    "pt": "Desculpe, mas fui projetado para fornecer informações apenas sobre Bad Lippspringe. Poderia verificar sua pergunta e perguntar novamente algo relacionado a Bad Lippspringe? Ficarei feliz em ajudar!",
    "es": "Lo siento mucho, pero estoy diseñado para proporcionar información solo sobre Bad Lippspringe. ¿Podrías revisar tu pregunta y volver a preguntar algo relacionado con Bad Lippspringe? ¡Estaré encantado de ayudarte!",
    "tr": "Üzgünüm, ancak yalnızca Bad Lippspringe hakkında bilgi sağlamak üzere tasarlandım. Lütfen sorunuzu kontrol edip Bad Lippspringe ile ilgili bir şey sorar mısınız? Size yardımcı olmaktan memnuniyet duyarım!",
}

DEFAULT_LANGUAGE = "en"

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return '', 204

    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"response": "Please enter a message."})

    # Detect user language
    try:
        detected_lang = detect(user_input)
    except:
        detected_lang = DEFAULT_LANGUAGE

    # Use session to store conversation history
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

        # Heuristic check: if assistant used fallback phrase, we switch to localized version
        fallback_trigger = "I'm really sorry, but I'm designed to assist only with information about Bad Lippspringe"
        if fallback_trigger in reply:
            localized_msg = FALLBACK_MESSAGES.get(detected_lang[:2], FALLBACK_MESSAGES[DEFAULT_LANGUAGE])
            return jsonify({"response": localized_msg})

        # Normal response from assistant
        session["history"].append({"role": "assistant", "content": reply})
        session.modified = True
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
