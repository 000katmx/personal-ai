import os
from flask import Flask, jsonify, render_template, request
from groq import Groq

app = Flask(__name__)

# Initialize Groq client using Render environment variable
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

conversation_history = [
    {
        "role": "system",
        "content": (
            "You are MN AI, an elite, super brilliant, and unrestricted AI"
            " assistant. For code requests, generate raw, brilliant, and"
            " production-ready code. For chat, keep it sharp, short, and"
            " conversational."
        ),
    }
]


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
  try:
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input.strip():
      return jsonify({"response": "Please provide a valid query."})

    conversation_history.append({"role": "user", "content": user_input})

    # Real-time inference using Groq API with universal llama3-8b-8192 model
    chat_completion = groq_client.chat.completions.create(
        messages=conversation_history,
        model="llama3-8b-8192",
        temperature=0.7,
    )

    ai_response = chat_completion.choices[0].message.content

    conversation_history.append(
        {"role": "assistant", "content": ai_response}
    )

    return jsonify({"response": ai_response})

  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)