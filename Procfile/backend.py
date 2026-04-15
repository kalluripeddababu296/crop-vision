"""
backend.py
----------
Flask REST API for the Crop Stress and Quality Detection System.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from image_processing import analyze_image
from scoring import classify_stress, calculate_health_score, generate_recommendations

import os

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------------------------
# Home Route
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Crop Stress Detection API is running",
        "endpoints": {
            "/health": "GET",
            "/analyze": "POST (image + parameters)"
        }
    })


# ---------------------------------------------------------------------------
# Health-check endpoint
# ---------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Crop Stress API is running."
    })


# ---------------------------------------------------------------------------
# Main analysis endpoint
# ---------------------------------------------------------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    # -----------------------------
    # 1. Validate image
    # -----------------------------
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files["image"]

    if image_file.filename == "":
        return jsonify({"error": "Empty image file"}), 400

    # -----------------------------
    # 2. Get inputs
    # -----------------------------
    try:
        temperature = float(request.form.get("temperature", 25))
        humidity = float(request.form.get("humidity", 60))
        soil_moisture = float(request.form.get("soil_moisture", 50))
    except:
        return jsonify({"error": "Invalid numeric input"}), 400

    # -----------------------------
    # 3. Validate ranges
    # -----------------------------
    if not (0 <= humidity <= 100):
        return jsonify({"error": "Humidity must be 0–100"}), 400

    if not (0 <= soil_moisture <= 100):
        return jsonify({"error": "Soil moisture must be 0–100"}), 400

    if not (-20 <= temperature <= 60):
        return jsonify({"error": "Temperature must be -20 to 60°C"}), 400

    # -----------------------------
    # 4. Image processing
    # -----------------------------
    image_bytes = image_file.read()
    img_result = analyze_image(image_bytes)

    if "error" in img_result:
        return jsonify(img_result), 422

    # Extract values
    green_score = img_result["green_score"]
    yellow_pct = img_result["yellow_percentage"]
    brown_pct = img_result["brown_percentage"]
    is_blurry = img_result["is_blurry"]
    blur_score = img_result["blur_score"]

    # -----------------------------
    # 5. Stress classification
    # -----------------------------
    stress_level = classify_stress(green_score)

    # -----------------------------
    # 6. Health score
    # -----------------------------
    health_score = calculate_health_score(
        green_score=green_score,
        soil_moisture=soil_moisture,
        temperature=temperature,
        humidity=humidity
    )

    # -----------------------------
    # 7. Recommendations
    # -----------------------------
    recommendations = generate_recommendations(
        stress_level=stress_level,
        soil_moisture=soil_moisture,
        temperature=temperature,
        humidity=humidity,
        yellow_pct=yellow_pct,
        brown_pct=brown_pct
    )

    # -----------------------------
    # 8. Final response
    # -----------------------------
    return jsonify({
        "stress_level": stress_level,
        "health_score": health_score,
        "recommendations": recommendations,

        "image_analysis": {
            "green_score": float(green_score),
            "green_percentage": float(img_result["green_percentage"]),
            "yellow_percentage": float(yellow_pct),
            "brown_percentage": float(brown_pct),
        },

        "environmental_inputs": {
            "temperature": float(temperature),
            "humidity": float(humidity),
            "soil_moisture": float(soil_moisture),
        },

        "blur_warning": bool(is_blurry),
        "blur_score": float(blur_score)
    })


# ---------------------------------------------------------------------------
# Run server (LOCAL only)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print(" Crop Stress Detection API  →  http://127.0.0.1:5000")
    print("=" * 55)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)