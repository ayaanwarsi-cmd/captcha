from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import base64
import os

app = Flask(__name__)
CORS(app)

# 🔑 API KEY from environment (IMPORTANT)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

@app.route("/")
def home():
    return "Captcha Server Running 🚀"

@app.route("/solve", methods=["POST"])
def solve():
    try:
        file = request.files["file"]
        img_bytes = file.read()

        b64 = base64.b64encode(img_bytes).decode()

        response = client.chat.completions.create(
            model="qwen/qwen2.5-vl-7b-instruct:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Read this captcha and return ONLY the exact 6 characters."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64}"
                            }
                        }
                    ]
                }
            ]
        )

        text = response.choices[0].message.content.strip()
        clean = ''.join(filter(str.isalnum, text))[:6].upper()

        return jsonify({
            "guesses": [clean, "------", "------"]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "guesses": ["ERROR", "ERROR", "ERROR"]
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))