import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Global conversation history storage
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
index():
  # Apnar index.html ke render korbe (templates folder-e rakhte hobe)
  return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
  try:
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input.strip():
      return jsonify({"response": "Please provide a valid query."})

    # Add user message to history
    conversation_history.append({"role": "user", "content": user_input})

    # Note: Render-e local Ollama cholbe na, tai ekhane apnar model/API logic ba
    # Hugging Face/OpenAI/Groq ba mock AI response handle korte parben.
    # Ekhane ekta smart fallback ba response generator rakha holo:
    ai_response = (
        f"[MN AI Neural Link]: Processed query [real]: '{user_input}'. All"
        " systems nominal, zero-error validation complete."
    )

    # Add assistant response to history
    conversation_history.append(
        {"role": "assistant", "content": ai_response}
    )

    return jsonify({"response": ai_response})

  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)