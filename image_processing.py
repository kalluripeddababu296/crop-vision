"""
image_processing.py
-------------------
Handles all OpenCV-based image analysis for the crop stress detection system.
Extracts green intensity, detects yellow/brown stress regions, and computes
a green score used for health assessment.
"""

import cv2
import numpy as np


def check_image_blur(image_bgr: np.ndarray) -> dict:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    is_blurry = bool(blur_score < 80.0)

    return {
        "is_blurry": is_blurry,
        "blur_score": float(round(blur_score, 2))
    }


def extract_color_features(image_bgr: np.ndarray) -> dict:
    """
    Analyse the crop image in HSV color space to:
      1. Measure healthy green coverage
      2. Detect stressed yellow / brown regions

    HSV ranges (OpenCV uses H: 0-179, S: 0-255, V: 0-255):
      - Green  : H 35-85,  S > 40, V > 40
      - Yellow : H 20-34,  S > 60, V > 60
      - Brown  : H 5-20,   S > 40, V 30-180

    Args:
        image_bgr: Image loaded by OpenCV (BGR format)

    Returns:
        dict containing pixel percentages and the final green_score (0-100)
    """
    # Convert to HSV — much easier to isolate hues than in BGR
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    total_pixels = image_bgr.shape[0] * image_bgr.shape[1]

    # --- Green mask ---
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    green_pixels = cv2.countNonZero(green_mask)

    # --- Yellow mask (early stress indicator) ---
    lower_yellow = np.array([20, 60, 60])
    upper_yellow = np.array([34, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    yellow_pixels = cv2.countNonZero(yellow_mask)

    # --- Brown mask (advanced stress / dead tissue) ---
    lower_brown = np.array([5, 40, 30])
    upper_brown = np.array([20, 255, 180])
    brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
    brown_pixels = cv2.countNonZero(brown_mask)

    # Compute percentages
    green_pct  = (green_pixels  / total_pixels) * 100
    yellow_pct = (yellow_pixels / total_pixels) * 100
    brown_pct  = (brown_pixels  / total_pixels) * 100

    # --- Green Score (0-100) ---
    # Start from green coverage; penalise yellow (mild) and brown (severe) areas
    raw_score = green_pct - (yellow_pct * 0.5) - (brown_pct * 1.0)
    green_score = max(0.0, min(100.0, raw_score))

    return {
        "green_percentage":  round(green_pct,  2),
        "yellow_percentage": round(yellow_pct, 2),
        "brown_percentage":  round(brown_pct,  2),
        "green_score":       round(green_score, 2),
        "total_pixels":      total_pixels
    }


def analyze_image(image_bytes: bytes) -> dict:
    """
    Full pipeline: decode → blur check → color feature extraction.

    Args:
        image_bytes: Raw bytes of the uploaded image file

    Returns:
        Combined dict with blur info + color features, or an error key
    """
    # Decode image from raw bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return {"error": "Could not decode image. Please upload a valid JPG/PNG file."}

    # Resize to a standard analysis size to keep processing fast
    image = cv2.resize(image, (512, 512))

    blur_info    = check_image_blur(image)
    color_info   = extract_color_features(image)

    return {**blur_info, **color_info}
