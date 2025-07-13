from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

HUGGINGFACE_API_KEY = "hf_..."  # 🔐 Vercelの環境変数にも可

@app.route("/", methods=["POST"])
def generate_image():
    prompt = request.json.get("prompt", "a cute Eevee sleeping")

    # HuggingFace API を使って画像生成
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
    }
    response = requests.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2",
        headers=headers,
        json={"inputs": prompt}
    )

    image_bytes = response.content
    img = Image.open(BytesIO(image_bytes))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    base64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return jsonify({ "base64Image": base64_str })
