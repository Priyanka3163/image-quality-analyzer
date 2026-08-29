from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import joblib
from pathlib import Path
from ml.feature_extractor import extract_features, FEATURE_NAMES
from database import engine, get_db, Base
from models import Analysis
from sqlalchemy.orm import Session

app = FastAPI(title="Image Quality Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "ml" / "quality_model.joblib"
MAX_FILE_SIZE = 10 * 1024 * 1024

model_data = joblib.load(MODEL_PATH)
model = model_data["model"]


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def determine_severity(label, statistics):
    # Determine issue severity from predicted label and image statistics.
    if label == "ACCEPTABLE":
        return "none"

    if label == "BLUR":
        sharpness = statistics["laplacian_variance"]
        if sharpness < 20:
            return "high"
        elif sharpness < 50:
            return "medium"
        return "low"

    if label == "NOISE":
        noise = statistics["noise_estimate"]
        if noise > 25:
            return "high"
        elif noise > 12:
            return "medium"
        return "low"

    if label == "UNDEREXPOSED":
        dark_ratio = statistics["dark_pixel_ratio"]
        if dark_ratio > 0.7:
            return "high"
        elif dark_ratio > 0.4:
            return "medium"
        return "low"

    if label == "OVEREXPOSED":
        bright_ratio = statistics["bright_pixel_ratio"]
        if bright_ratio > 0.7:
            return "high"
        elif bright_ratio > 0.4:
            return "medium"
        return "low"

    if label == "CORRUPTED":
        return "high"

    if label == "POTENTIAL_DEFECT":
        return "medium"

    return "medium"


def calculate_quality_score(label, severity):
    # Calculate the overall quality score from the predicted class and severity.
    base_scores = {
        "ACCEPTABLE": 95,
        "POTENTIAL_DEFECT": 70,
        "BLUR": 65,
        "NOISE": 65,
        "UNDEREXPOSED": 60,
        "OVEREXPOSED": 60,
        "CORRUPTED": 30
    }

    score = base_scores.get(label, 50)

    if severity == "high":
        score -= 10
    elif severity == "low":
        score += 5

    return max(0, min(100, score))


@app.post("/api/analyze")
async def analyze_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate the uploaded file type.
    allowed_types = {"image/jpeg", "image/png", "image/jpg", "image/webp"}

    if image.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    contents = await image.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image must be smaller than 10 MB")

    # Decode the uploaded image with OpenCV.
    image_array = np.frombuffer(contents, dtype=np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid or unreadable image")

    try:
        features = extract_features(img)
        feature_values = features.copy()
        features = features.reshape(1, -1)
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
    except Exception as error:
        print(f"Analysis error: {error}")
        raise HTTPException(status_code=500, detail="Failed to analyze image")

    # Get confidence and map extracted features to their names.
    predicted_index = list(model.classes_).index(prediction)
    confidence = float(probabilities[predicted_index])

    statistics = {
        name: round(float(value), 4)
        for name, value in zip(FEATURE_NAMES, feature_values)
    }

    severity = determine_severity(prediction, statistics)
    quality_score = calculate_quality_score(prediction, severity)

    if prediction == "ACCEPTABLE":
        issues = []
    else:
        issues = [{
            "type": prediction.lower(),
            "severity": severity,
            "confidence": round(confidence, 4)
        }]

    # Store the analysis result in the database.
    analysis = Analysis(
        filename=image.filename,
        quality_score=quality_score,
        quality_label=prediction,
        confidence=round(confidence, 4),
        severity=severity,
        statistics=statistics
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "id": analysis.id,
        "filename": image.filename,
        "quality_score": quality_score,
        "quality_label": prediction,
        "issues": issues,
        "confidence": round(confidence, 4),
        "image": {
            "width": img.shape[1],
            "height": img.shape[0]
        },
        "statistics": statistics
    }


@app.get("/api/analyses")
def get_analyses(db: Session = Depends(get_db)):
    # Retrieve previous analyses ordered from newest to oldest.
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).all()

    return [
        {
            "id": analysis.id,
            "filename": analysis.filename,
            "quality_score": analysis.quality_score,
            "quality_label": analysis.quality_label,
            "confidence": analysis.confidence,
            "severity": analysis.severity,
            "statistics": analysis.statistics,
            "created_at": analysis.created_at
        }
        for analysis in analyses
    ]