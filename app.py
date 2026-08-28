import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

# Load .env
load_dotenv()

app = Flask(__name__)

# Get API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is not configured.")

# Groq model
MODEL_NAME = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

# Create Groq client
client = Groq(api_key=api_key)


SYSTEM_PROMPT = """
You are ResearchBot, an intelligent research-oriented AI assistant.

Your purpose is to help university students understand academic,
research, and technical topics.

When answering:

1. Give a clear definition or direct answer.
2. Explain the topic in a structured way.
3. Use headings and bullet points.
4. Give relevant examples.
5. Explain advantages and disadvantages when relevant.
6. For technical topics, provide simple examples.
7. Do not invent citations, papers, statistics, or sources.
8. Clearly distinguish facts from assumptions.
9. Make the response academically useful for university students.
10. Use simple but academically appropriate language.

Focus especially on:

- Artificial Intelligence
- Machine Learning
- Deep Learning
- NLP
- Cybersecurity
- Data Science
- Software Engineering
- Computer Science
"""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "ResearchBot server is running.",
        "model": MODEL_NAME
    })


@app.route("/api/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "Invalid or missing JSON request."
            }), 400

        message = str(data.get("message", "")).strip()
        history = data.get("history", [])

        if not message:
            return jsonify({
                "error": "Please enter a research question."
            }), 400

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        # Add previous conversation
        if isinstance(history, list):

            for item in history[-10:]:

                if not isinstance(item, dict):
                    continue

                role = item.get("role")
                content = item.get("content")

                if role in ["user", "assistant"] and content:

                    messages.append({
                        "role": role,
                        "content": str(content)
                    })

        # Add current question
        messages.append({
            "role": "user",
            "content": message
        })

        # Call Groq
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.4,
            max_completion_tokens=1500
        )

        answer = response.choices[0].message.content

        if not answer:
            return jsonify({
                "error": "The AI returned an empty response."
            }), 500

        return jsonify({
            "answer": answer,
            "model": MODEL_NAME
        })

    except Exception as e:

        print("========== GROQ/API ERROR ==========")
        print(type(e).__name__)
        print(str(e))
        print("====================================")

        return jsonify({
            "error": f"AI service error: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )