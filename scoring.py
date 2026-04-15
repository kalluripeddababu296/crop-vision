"""
scoring.py
----------
Contains all the logic for:
  - Stress level classification (Low / Medium / High)
  - Health score calculation (0-100) using a weighted formula
  - Recommendation engine (rule-based)
"""

from typing import Tuple


# ---------------------------------------------------------------------------
# 1. STRESS LEVEL CLASSIFICATION
# ---------------------------------------------------------------------------

def classify_stress(green_score: float) -> str:
    """
    Map the green_score from image analysis to a human-readable stress level.

    Thresholds:
      green_score >= 50  → Low Stress   (plant looks healthy)
      green_score 20-49  → Medium Stress (some yellowing/browning visible)
      green_score < 20   → High Stress  (significant discolouration)

    Args:
        green_score: 0-100 value from image_processing

    Returns:
        One of: "Low", "Medium", "High"
    """
    if green_score >= 50:
        return "Low"
    elif green_score >= 20:
        return "Medium"
    else:
        return "High"


# ---------------------------------------------------------------------------
# 2. HEALTH SCORE CALCULATION
# ---------------------------------------------------------------------------

def calculate_health_score(
    green_score: float,
    soil_moisture: float,
    temperature: float,
    humidity: float
) -> float:
    """
    Compute an overall health score (0-100) using a weighted formula that
    combines visual greenness with environmental sensor data.

    Weights:
      - Green score    : 50 % (most important — direct visual indicator)
      - Soil moisture  : 25 % (normalised to 0-100 scale)
      - Temperature    : 15 % (ideal ~25 °C; score drops away from ideal)
      - Humidity       : 10 % (ideal ~60 %; very high humidity penalised slightly)

    Args:
        green_score   : 0-100 from image analysis
        soil_moisture : 0-100 % (sensor reading)
        temperature   : degrees Celsius
        humidity      : 0-100 % relative humidity

    Returns:
        health_score as float 0-100
    """

    # --- Soil moisture sub-score (0-100) ---
    # Ideal range: 40-70 %. Penalise extremes.
    moisture_score = soil_moisture  # Already on 0-100 scale

    # --- Temperature sub-score (0-100) ---
    # Ideal temperature = 25 °C; score drops linearly beyond ±10 °C
    ideal_temp = 25.0
    temp_deviation = abs(temperature - ideal_temp)
    temp_score = max(0.0, 100.0 - (temp_deviation * 4.0))

    # --- Humidity sub-score (0-100) ---
    # Ideal humidity ~60 %; penalise very high (>80 %) and very low (<30 %)
    if 30 <= humidity <= 80:
        humidity_score = 100.0 - abs(humidity - 60) * 1.5
    else:
        humidity_score = max(0.0, 100.0 - abs(humidity - 60) * 3.0)

    # --- Weighted combination ---
    health_score = (
        (green_score    * 0.50) +
        (moisture_score * 0.25) +
        (temp_score     * 0.15) +
        (humidity_score * 0.10)
    )

    return round(max(0.0, min(100.0, health_score)), 1)


# ---------------------------------------------------------------------------
# 3. RECOMMENDATION ENGINE
# ---------------------------------------------------------------------------

def generate_recommendations(
    stress_level: str,
    soil_moisture: float,
    temperature: float,
    humidity: float,
    yellow_pct: float,
    brown_pct: float
) -> list:
    """
    Rule-based recommendation engine. Returns a list of actionable advice
    strings ordered by priority.

    Rules (evaluated independently so multiple can fire):
      1. Low moisture → water immediately
      2. Very low moisture → critical irrigation alert
      3. High humidity → fungal disease risk
      4. High temperature → heat stress mitigation
      5. Low temperature → frost / cold stress
      6. High yellow % → nutrient deficiency possible
      7. High brown % → possible disease / severe stress
      8. Low stress, all good → positive reinforcement

    Args:
        stress_level  : "Low" / "Medium" / "High"
        soil_moisture : 0-100 %
        temperature   : °C
        humidity      : 0-100 %
        yellow_pct    : % yellow pixels in image
        brown_pct     : % brown pixels in image

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # --- Water / Moisture ---
    if soil_moisture < 20:
        recommendations.append(
            "🚨 Critical: Soil moisture is very low. Irrigate immediately to prevent wilting."
        )
    elif soil_moisture < 40:
        recommendations.append(
            "💧 Increase watering. Soil moisture is below optimal levels (< 40 %)."
        )
    elif soil_moisture > 85:
        recommendations.append(
            "⚠️ Soil is waterlogged. Reduce irrigation and ensure proper drainage."
        )

    # --- Humidity / Fungal risk ---
    if humidity > 80:
        recommendations.append(
            "🍄 High humidity detected (> 80 %). Monitor for fungal diseases "
            "(e.g., powdery mildew, blight). Improve air circulation."
        )
    elif humidity < 25:
        recommendations.append(
            "💨 Very low humidity. Consider misting or using a humidifier for sensitive crops."
        )

    # --- Temperature ---
    if temperature > 35:
        recommendations.append(
            "🌡️ Heat stress risk. Temperature exceeds 35 °C. "
            "Provide shade, increase watering frequency, and mulch soil."
        )
    elif temperature > 30:
        recommendations.append(
            "☀️ Elevated temperature (> 30 °C). Ensure adequate watering and consider afternoon shading."
        )
    elif temperature < 10:
        recommendations.append(
            "🥶 Cold stress risk. Temperature below 10 °C. "
            "Protect plants with frost cloth or move to a warmer location."
        )

    # --- Visual stress indicators ---
    if yellow_pct > 25:
        recommendations.append(
            "🟡 Significant yellowing detected. Possible causes: nitrogen deficiency, "
            "overwatering, or early disease. Consider soil nutrient testing."
        )
    elif yellow_pct > 10:
        recommendations.append(
            "🟡 Mild yellowing visible. Monitor closely and check soil nutrient levels."
        )

    if brown_pct > 20:
        recommendations.append(
            "🟤 Substantial brown/dead tissue detected. This may indicate severe drought, "
            "disease, or root damage. Inspect roots and consult an agronomist."
        )
    elif brown_pct > 10:
        recommendations.append(
            "🟤 Some browning detected. Check for pest damage, disease, or heat scorch."
        )

    # --- Positive message if everything looks fine ---
    if not recommendations and stress_level == "Low":
        recommendations.append(
            "✅ Crop appears healthy! Maintain current irrigation and environmental conditions."
        )

    # --- Generic advice for medium/high stress with no specific trigger ---
    if not recommendations and stress_level == "Medium":
        recommendations.append(
            "⚠️ Moderate stress detected. Review watering schedule and check for early signs of disease."
        )

    if not recommendations and stress_level == "High":
        recommendations.append(
            "🚨 High stress detected. Immediate attention needed — inspect soil, roots, and foliage."
        )

    return recommendations
