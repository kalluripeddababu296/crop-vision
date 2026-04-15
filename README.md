# 🌿 Crop Stress and Quality Detection System

A simple, fully working web application to detect crop stress levels and health
scores from leaf/crop images combined with environmental sensor data.

---

## 📁 Project Structure

```
crop_stress_system/
│
├── app.py                  ← Streamlit frontend UI
├── backend.py              ← Flask REST API
├── image_processing.py     ← OpenCV image analysis
├── scoring.py              ← Stress classification, health score, recommendations
├── requirements.txt        ← All Python dependencies
└── README.md               ← This file
```

---

## ⚙️ Setup Instructions (Anaconda)

### Step 1 — Create a conda environment

```bash
conda create -n cropstress python=3.10 -y
conda activate cropstress
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Note for Windows users:** If `opencv-python` fails, try:
> `pip install opencv-python-headless`

---

## 🚀 Running the Application

You need **two terminals** open simultaneously.

### Terminal 1 — Start the Flask backend

```bash
conda activate cropstress
cd crop_stress_system
python backend.py
```

You should see:
```
=======================================================
  Crop Stress Detection API  |  http://127.0.0.1:5000
=======================================================
 * Running on http://0.0.0.0:5000
```

### Terminal 2 — Start the Streamlit frontend

```bash
conda activate cropstress
cd crop_stress_system
streamlit run app.py
```

A browser tab will open automatically at `http://localhost:8501`

---

## 🖥️ How to Use

1. Upload a crop or leaf photo (JPG / PNG)
2. Optionally toggle **Auto-fetch Weather** to pull live temperature & humidity
3. Adjust the sliders for Temperature, Humidity, and Soil Moisture
4. Click **Analyze Crop Health**
5. View your results:
   - **Stress Level** badge (Low / Medium / High)
   - **Health Score** (0–100)
   - **Color analysis** breakdown (green, yellow, brown %)
   - **Recommendations** tailored to your inputs

---

## 🔬 How It Works

### Image Processing (`image_processing.py`)
- Loads the image with **OpenCV**
- Runs a **blur detection** check (Laplacian variance)
- Converts to **HSV color space** (much better for isolating plant hues)
- Creates three color masks:
  | Color  | HSV Hue Range | Meaning                  |
  |--------|---------------|--------------------------|
  | Green  | 35 – 85       | Healthy tissue           |
  | Yellow | 20 – 34       | Early stress / chlorosis |
  | Brown  | 5 – 20        | Dead tissue / disease    |
- **Green Score** = green% − 0.5×yellow% − 1.0×brown% (clamped 0–100)

### Stress Classification (`scoring.py → classify_stress`)
| Green Score | Stress Level |
|-------------|--------------|
| ≥ 50        | Low          |
| 20 – 49     | Medium       |
| < 20        | High         |

### Health Score Formula
```
health_score = (green_score × 0.50)
             + (soil_moisture × 0.25)
             + (temperature_score × 0.15)
             + (humidity_score × 0.10)
```
- **temperature_score**: 100 − 4 × |temperature − 25| (ideal = 25 °C)
- **humidity_score**: 100 − 1.5 × |humidity − 60| (ideal = 60 %)

### Recommendation Engine
Rule-based system — multiple rules can fire simultaneously:

| Condition              | Recommendation                          |
|------------------------|-----------------------------------------|
| Soil moisture < 20 %   | 🚨 Irrigate immediately                 |
| Soil moisture 20–40 %  | 💧 Increase watering                    |
| Soil moisture > 85 %   | ⚠️ Reduce irrigation / improve drainage |
| Humidity > 80 %        | 🍄 Fungal disease risk                  |
| Temperature > 35 °C    | 🌡️ Heat stress — shade & water          |
| Temperature < 10 °C    | 🥶 Cold stress — frost protection       |
| Yellow pixels > 25 %   | 🟡 Possible nitrogen deficiency         |
| Brown pixels > 20 %    | 🟤 Severe stress / disease              |

### Optional — Live Weather (Open-Meteo)
- Free API, no key required
- Fetches `temperature_2m` and `relative_humidity_2m` for a given lat/lon
- Defaults to Tamil Nadu, India coordinates; change in `app.py → fetch_weather_openmeteo()`

---

## 🔌 API Reference

### `POST /analyze`

**Request:** `multipart/form-data`

| Field          | Type   | Description                      |
|----------------|--------|----------------------------------|
| image          | file   | JPG or PNG crop/leaf photo       |
| temperature    | float  | Air temperature in °C            |
| humidity       | float  | Relative humidity 0–100 %        |
| soil_moisture  | float  | Soil water content 0–100 %       |

**Response:** `application/json`

```json
{
  "stress_level": "Medium",
  "health_score": 62.4,
  "recommendations": ["💧 Increase watering..."],
  "image_analysis": {
    "green_score": 38.5,
    "green_percentage": 42.1,
    "yellow_percentage": 11.2,
    "brown_percentage": 5.8
  },
  "environmental_inputs": {
    "temperature_c": 28.0,
    "humidity_pct": 72.0,
    "soil_moisture_pct": 35.0
  },
  "blur_warning": false,
  "blur_score": 312.4
}
```

### `GET /health`

Returns `{"status": "ok"}` — use to verify the server is running.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `ConnectionError` in Streamlit | Make sure `python backend.py` is running in Terminal 1 |
| `ModuleNotFoundError: cv2` | Run `pip install opencv-python` (or `opencv-python-headless`) |
| Streamlit page not opening | Go to `http://localhost:8501` manually in your browser |
| Weather fetch fails | Normal on restricted networks — just enter values manually |

---

## 📜 License
MIT — free to use and modify.
