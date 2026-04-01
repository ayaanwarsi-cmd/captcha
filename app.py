from flask import Flask, request, jsonify
import numpy as np
import cv2
import tensorflow as tf

app = Flask(__name__)

model = tf.keras.models.load_model("model.h5")

CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
num_to_char = {i:c for i,c in enumerate(CHARS)}

@app.route("/solve", methods=["POST"])
def solve():
    file = request.files["file"]
    img_bytes = file.read()

    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    img = cv2.resize(img, (200,80))

    img = cv2.GaussianBlur(img, (3,3), 0)
    _, img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)

    img = img / 255.0
    img = img.reshape(1,80,200,1)

    pred = model.predict(img)[0]

    result = ""
    for i in pred:
        result += num_to_char[np.argmax(i)]

    return jsonify({"guesses": [result, "------", "------"]})

app.run(port=5000)
