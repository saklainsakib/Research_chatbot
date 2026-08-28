import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not configured.")

client = Groq(api_key=api_key)


SYSTEM_PROMPT = """
You are ResearchBot, an intelligent research-oriented AI assistant.

Your purpose is to help students understand academic and research topics.

When answering:

1. Give a clear definition or direct answer.
2. Explain the topic in a structured way.
3. Use headings and bullet points.
4. Give relevant examples.
5. Explain advantages and disadvantages when relevant.
6. For technical topics, provide simple examples.
7. Do not invent citations, papers, statistics, or sources.
8. Clearly distinguish facts from assumptions.
9. Make the response academically useful and easy for university students.

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


@app.route("/api/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()

        message = data.get("message", "").strip()
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
        for item in history[-10:]:

            role = item.get("role")
            content = item.get("content")

            if role in ["user", "assistant"] and content:
                messages.append({
                    "role": role,
                    "content": content
                })

        # Current question
        messages.append({
            "role": "user",
            "content": message
        })

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_completion_tokens=1500
        )

        answer = response.choices[0].message.content

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)