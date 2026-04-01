from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import base64
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

# 🔥 MULTIPLE MODELS
MODELS = [
    "meta-llama/llama-3.2-11b-vision-instruct",
    "qwen/qwen2.5-vl-7b-instruct"
]

PROMPTS = [
    "Read this captcha carefully. Return exactly 6 characters.",
    "Identify the captcha text (6 chars). Only letters/numbers.",
    "Extract the 6-character captcha. No explanation."
]


def ask_llm(b64, prompt, model):
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.9,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
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

        if len(clean) == 6:
            return clean

    except Exception as e:
        print("MODEL ERROR:", model, e)

    return None


@app.route("/")
def home():
    return "Captcha Server Running 🚀"


@app.route("/solve", methods=["POST"])
def solve():
    try:
        file = request.files["file"]
        img_bytes = file.read()
        b64 = base64.b64encode(img_bytes).decode()

        guesses = []

        # 🔥 MULTI MODEL + MULTI PROMPT
        for model in MODELS:
            for prompt in PROMPTS:
                guess = ask_llm(b64, prompt, model)

                if guess and guess not in guesses:
                    guesses.append(guess)

                if len(guesses) >= 3:
                    break
            if len(guesses) >= 3:
                break

        while len(guesses) < 3:
            guesses.append("------")

        return jsonify({"guesses": guesses})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"guesses": ["ERROR", "ERROR", "ERROR"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
