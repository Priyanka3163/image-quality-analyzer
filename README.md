# AI Image Quality Analyzer

An AI-powered full-stack application that analyzes uploaded images and evaluates their visual quality using computer vision and a machine-learning classifier.

The system accepts an image, extracts interpretable image-quality features, uses a trained Random Forest classifier to identify the image-quality condition, calculates severity and an overall quality score, and stores the analysis for later viewing.

**Image Upload → Validation → Feature Extraction → ML Classification → Quality Assessment → Database Storage → Web Interface**

---

## 1. Project Overview

The goal of this project is to automatically identify common image-quality problems without relying on external AI or computer-vision APIs.

The application currently detects seven quality categories:

* Blur / insufficient sharpness
* Underexposure
* Overexposure
* Image noise
* Severe image corruption
* Potential visual defect
* Acceptable image quality

The project uses a **classical machine-learning approach with engineered computer-vision features**. This was selected because the relevant image-quality characteristics, such as sharpness, brightness, noise, contrast, and texture, can be represented using interpretable numerical features.

---

## 2. Key Features

### Image Analysis

* Upload JPG, JPEG, PNG, and WebP images
* Client-side file validation
* Maximum upload size of 10 MB
* Image preview before analysis
* OpenCV-based image decoding
* 16 engineered image-quality features
* Random Forest quality classification
* Prediction confidence
* Severity estimation
* Overall quality score
* Image dimensions
* Feature statistics returned with the analysis

### Quality Detection

* `ACCEPTABLE`
* `BLUR`
* `UNDEREXPOSED`
* `OVEREXPOSED`
* `NOISE`
* `CORRUPTED`
* `POTENTIAL_DEFECT`

### Application

* React-based web interface
* Analysis result page
* Analysis history page
* REST API using FastAPI
* SQLite persistence
* Dockerized frontend and backend
* Docker Compose deployment
* Backend health-check endpoint
* Error handling for invalid uploads
* Protection against repeated analysis submissions

---

# 3. System Architecture

```text
                         ┌─────────────────────────┐
                         │       React Frontend     │
                         │                         │
                         │  Image Upload           │
                         │  Image Preview          │
                         │  Analysis Results       │
                         │  Analysis History       │
                         └────────────┬────────────┘
                                      │
                                HTTP / REST
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │       FastAPI Backend    │
                         │                         │
                         │  File Validation        │
                         │  Image Decoding         │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    Feature Extraction   │
                         │                         │
                         │  Brightness             │
                         │  Contrast               │
                         │  Sharpness              │
                         │  Edge Density           │
                         │  Noise                  │
                         │  Saturation             │
                         │  Texture                │
                         │  Entropy                │
                         │  Regional Statistics    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   Random Forest Model    │
                         │                         │
                         │ quality_model.joblib    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    Quality Assessment    │
                         │                         │
                         │  Predicted Class        │
                         │  Confidence             │
                         │  Severity               │
                         │  Quality Score          │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      SQLite Database     │
                         │                         │
                         │    Analysis History     │
                         └─────────────────────────┘
```

---

# 4. Machine Learning Approach

## 4.1 Model Selection

The project uses a **Random Forest classifier** trained on engineered image-quality features.

A classical machine-learning approach was chosen because the problem is strongly related to measurable image statistics.

For example:

* Blur can be associated with reduced Laplacian variance.
* Underexposure can be associated with a high proportion of dark pixels.
* Overexposure can be associated with a high proportion of bright pixels.
* Noise can be estimated from high-frequency residuals.
* Texture can be represented using local variance.
* Contrast can be represented using the image's dynamic range.

Random Forest was selected because it:

* Handles nonlinear relationships between features.
* Works well with relatively small tabular datasets.
* Does not require feature scaling.
* Provides feature-importance information.
* Produces class probabilities that can be used as prediction confidence.

---

## 4.2 Feature Extraction

The feature extractor is implemented in:

```text
backend/ml/feature_extractor.py
```

The system extracts 16 features from each image.

| Feature                   | Purpose                                        |
| ------------------------- | ---------------------------------------------- |
| `brightness_mean`         | Average image brightness                       |
| `brightness_std`          | Variation in brightness                        |
| `dark_pixel_ratio`        | Proportion of very dark pixels                 |
| `bright_pixel_ratio`      | Proportion of very bright pixels               |
| `dynamic_range`           | Approximate contrast / intensity range         |
| `laplacian_variance`      | Sharpness measurement                          |
| `edge_density`            | Amount of detected edges                       |
| `noise_estimate`          | High-frequency noise estimate                  |
| `saturation_mean`         | Average color saturation                       |
| `saturation_std`          | Saturation variation                           |
| `high_saturation_ratio`   | Proportion of highly saturated pixels          |
| `texture_mean`            | Average local image variance                   |
| `texture_std`             | Variation in local texture                     |
| `entropy`                 | Grayscale information/complexity               |
| `regional_mean_variation` | Difference in brightness between image regions |
| `regional_std_variation`  | Difference in regional intensity variation     |

The resulting 16-dimensional feature vector is provided to the Random Forest model.

---

# 5. Dataset and Training

## 5.1 Source Dataset

The project uses the publicly available **Butterfly Image Classification** dataset as a source of clean images.

The dataset is used as a source of visually diverse images rather than as a butterfly-species classification dataset.

The project generates controlled image-quality degradations from these images to create training examples.

---

## 5.2 Synthetic Degradation

The dataset-generation pipeline is implemented in:

```text
backend/data/data_generation.py
```

For each selected source image, the pipeline can generate:

* Original / acceptable image
* Gaussian blur
* Underexposure
* Overexposure
* Gaussian noise
* Severe corruption
* Potential visual defect

The degradation parameters are randomized within predefined ranges so that generated samples are not identical.

Examples include:

### Blur

Gaussian blur with randomized kernel sizes and sigma values.

### Underexposure

Gamma correction with gamma values greater than 1 to darken the image.

### Overexposure

Gamma correction combined with intensity scaling to produce excessive brightness and clipping.

### Noise

Gaussian sensor-like noise with randomized noise strength.

### Corruption

A randomly selected image region is replaced with random pixel values, followed by aggressive JPEG compression.

### Potential Defect

A combination of strong blur, noise, and brightness distortion intended to represent a visually abnormal image.

> The `CORRUPTED` and `POTENTIAL_DEFECT` classes are currently synthetic approximations rather than models of specific real-world defect mechanisms.

---

## 5.3 Train/Test Data

The source dataset is split into separate training and testing images before quality degradations are generated.

The current development configuration uses a deliberately small subset of the available source images so that the complete training and application pipeline could be developed and tested within the assessment timeframe.

Current configuration:

```text
Training source images: 25
Testing source images: 5
```

Each source image produces examples for the quality categories, resulting in a substantially larger number of generated training samples than the number of original source images.

The data-generation script can be configured to use more source images by changing:

```python
MAX_TRAIN_IMAGES
MAX_TEST_IMAGES
```

Setting these values to `None` allows the pipeline to process the available images without this development-time limit.

---

# 6. Model Training

The training implementation is located at:

```text
backend/ml/train_model.py
```

The current Random Forest configuration is:

```python
RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
```

The model is trained using the extracted feature vectors and corresponding quality labels.

After training, the model is serialized using `joblib`:

```text
backend/ml/quality_model.joblib
```

The serialized model is loaded by the FastAPI backend when the application starts.

---

# 7. Model Evaluation

The training script evaluates the model against the held-out test split.

The following metrics are generated:

* Accuracy
* Precision
* Recall
* F1-score
* Confusion matrix
* Feature importance

The current development model achieved approximately:

**91.4% test accuracy**

This result should be interpreted in the context of the current dataset.

The evaluation set is based on synthetic image-quality degradations generated from a relatively small number of source images. Therefore, the result demonstrates that the selected features and classifier can distinguish the generated quality conditions, but it should **not be interpreted as evidence of production-level performance on arbitrary real-world images**.

A larger evaluation using unseen source images and real-world quality problems would provide a stronger measure of generalization.

---

# 8. Explainability

The application provides several interpretable components rather than treating the model as a complete black box.

### Feature Statistics

The API returns the extracted feature values for every analyzed image.

For example:

```json
{
    "laplacian_variance": 42.31,
    "dark_pixel_ratio": 0.12,
    "bright_pixel_ratio": 0.08,
    "noise_estimate": 6.74,
    "dynamic_range": 181.42
}
```

These values allow the user to understand characteristics of the analyzed image.

### Feature Importance

The training script also reports Random Forest feature importance, allowing the relative contribution of individual image-quality features to be inspected.

### Severity

After classification, the system uses the relevant image statistics to determine whether the detected issue is:

* `low`
* `medium`
* `high`

For example, blur severity is determined using the extracted Laplacian variance.

### Confidence

The Random Forest's class probability for the predicted class is returned as the prediction confidence.

---

# 9. Quality Score vs. Confidence

The application exposes two different concepts:

### Quality Score

The **quality score** is an overall 0–100 assessment of the image based on its predicted quality category and estimated severity.

It is displayed separately from model confidence.

### Confidence

**Confidence** represents the Random Forest's predicted probability for the selected quality category.

For example:

```text
Quality Score: 65 / 100
Prediction: BLUR
Confidence: 0.91
Severity: medium
```

A high confidence therefore does **not** necessarily mean that the image has a high quality score. It means the classifier is confident about its predicted category.

---

# 10. Backend API

The backend is implemented using **FastAPI**.

## Health Check

```http
GET /health
```

Example response:

```json
{
    "status": "healthy"
}
```

---

## Analyze Image

```http
POST /api/analyze
```

Accepts an image using multipart form data.

The endpoint:

1. Validates the uploaded file type.
2. Reads the uploaded bytes.
3. Decodes the image using OpenCV.
4. Rejects empty, invalid, or unreadable images.
5. Extracts the 16 image-quality features.
6. Runs the Random Forest classifier.
7. Calculates prediction confidence.
8. Determines issue severity.
9. Calculates the overall quality score.
10. Stores the result in SQLite.
11. Returns the analysis as structured JSON.

Example response:

```json
{
    "id": 1,
    "filename": "example.jpg",
    "quality_score": 65,
    "quality_label": "BLUR",
    "issues": [
        {
            "type": "blur",
            "severity": "medium",
            "confidence": 0.91
        }
    ],
    "confidence": 0.91,
    "image": {
        "width": 1920,
        "height": 1080
    },
    "statistics": {
        "brightness_mean": 121.42,
        "brightness_std": 48.31,
        "dark_pixel_ratio": 0.14,
        "bright_pixel_ratio": 0.07,
        "dynamic_range": 176.2,
        "laplacian_variance": 34.21,
        "edge_density": 0.082,
        "noise_estimate": 7.14,
        "saturation_mean": 87.21,
        "saturation_std": 54.31,
        "high_saturation_ratio": 0.03,
        "texture_mean": 421.51,
        "texture_std": 318.42,
        "entropy": 7.12,
        "regional_mean_variation": 12.31,
        "regional_std_variation": 8.14
    }
}
```

---

## Analysis History

```http
GET /api/analyses
```

Returns previously stored analyses ordered by creation time.

---

## Interactive API Documentation

When running locally, FastAPI's interactive documentation is available at:

```text
http://localhost:8000/docs
```

---

# 11. Database

The backend uses **SQLite with SQLAlchemy** to persist analysis results.

The database stores information including:

* Analysis ID
* Original filename
* Quality score
* Predicted quality label
* Prediction confidence
* Severity
* Extracted image statistics
* Analysis timestamp

The database is initialized automatically by the backend using SQLAlchemy.

The SQLite database file is created by the application and does not require a separate database server.

---

# 12. Frontend

The frontend is implemented using:

* React
* Vite
* React Router
* Tailwind CSS
* DaisyUI

## Home Page

The home page allows users to:

1. Select an image.
2. Validate the file.
3. Preview the image.
4. Start analysis.
5. Display an analysis/loading state.
6. View the final quality assessment.
7. View detected issues, severity, confidence, and image statistics.

---

## History Page

The history page retrieves previous analyses from:

```http
GET /api/analyses
```

Each history entry displays information such as:

* Filename
* Quality score
* Quality classification
* Confidence
* Severity
* Timestamp

---

# 13. Error Handling

The application validates input at both the frontend and backend levels.

Handled cases include:

* Unsupported image formats
* Files larger than 10 MB
* Empty uploads
* Invalid image files
* Unreadable images
* Backend/API connection failures
* Repeated analysis submissions while a request is already running

The frontend prevents repeated submissions while an analysis request is in progress.

The backend returns appropriate HTTP errors for invalid requests.

---

# 14. Project Structure

```text
image-quality-analyzer/
│
├── backend/
│   ├── ml/
│   │   ├── train_model.py
│   │   ├── feature_extractor.py
│   │   └── quality_model.joblib
│   │
│   ├── data/
│   │   └── data_generation.py
│   │
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── user/
│   │   │   ├── components/
│   │   │   │   ├── PlainNavbar.jsx
│   │   │   │   └── ImageUploader.jsx
│   │   │   └── pages/
│   │   │       ├── HomePage.jsx
│   │   │       └── HistoryPage.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── .env.example
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yaml
├── .gitignore
└── README.md
```

> Large generated datasets and development-only files are intentionally excluded from the repository where appropriate.

---

# 15. Running the Application with Docker

Docker Compose is the recommended way to run the complete application.

## Prerequisites

Install:

* Docker Desktop
* Docker Compose

No local Node.js installation is required when running the frontend through Docker.

---

## Start the Application

From the project root:

```bash
docker compose up --build
```

Or run in detached mode:

```bash
docker compose up --build -d
```

Docker Compose starts separate containers for the frontend and backend.

---

## Frontend

```text
http://localhost:5173
```

## Backend

```text
http://localhost:8000
```

## FastAPI Documentation

```text
http://localhost:8000/docs
```

## Health Check

```text
http://localhost:8000/health
```

---

## Stop the Application

```bash
docker compose down
```

---

# 16. Environment Configuration

The frontend uses an environment variable for the backend API URL.

Create:

```text
frontend/.env
```

using:

```text
frontend/.env.example
```

Example:

```env
VITE_API_URL=http://localhost:8000
```

Local environment files should not be committed to the repository.

---

# 17. Model Deployment and Inference

The trained model is included in:

```text
backend/ml/quality_model.joblib
```

When the FastAPI backend starts, the model is loaded into memory:

```python
model_data = joblib.load(MODEL_PATH)
model = model_data["model"]
```

For each uploaded image:

```text
Uploaded Image
      ↓
OpenCV decoding
      ↓
Feature Extraction
      ↓
16-dimensional feature vector
      ↓
Random Forest inference
      ↓
Predicted quality class
      ↓
Confidence + Severity + Quality Score
      ↓
Database
      ↓
JSON response
```

This means model inference does not require an external AI service or API key.

---

# 18. Reproducing the Training Pipeline

The training pipeline consists of two main stages.

### Step 1 — Generate the Dataset

Run:

```bash
python backend/data/data_generation.py
```

The script downloads the source dataset and generates the quality-degraded training and testing images.

### Step 2 — Train the Model

Run:

```bash
python backend/ml/train_model.py
```

The trained model is saved as:

```text
backend/ml/quality_model.joblib
```

The training script also prints the classification report, confusion matrix, accuracy, and feature importance.

> The included `.joblib` file allows the application to run inference without requiring the model to be retrained.

---

# 19. Current Limitations

This project is an assessment prototype rather than a production image-quality inspection system.

### Dataset Size

The current model was developed using a relatively small subset of the available source dataset to keep the training and experimentation cycle practical within the assessment timeframe.

### Synthetic Data

Most quality categories are generated using controlled image transformations rather than collected from real-world failure cases.

### Potential Defect Detection

`POTENTIAL_DEFECT` is currently a synthetic visual-anomaly category created using combined image degradations. It does not represent a specific domain-specific defect detector.

### Generalization

The current evaluation demonstrates performance on the generated test conditions. More diverse unseen images and real-world defective examples would be required to establish stronger generalization.

### Quality Score

The quality score is a rule-based interpretation of the predicted class and severity rather than a directly learned perceptual-quality score.

---

# 20. Future Improvements

Potential extensions include:

1. **Larger and more diverse training data**

   * Generate quality variations from thousands of source images.
   * Include more diverse image domains.

2. **Real-world quality-failure data**

   * Supplement synthetic degradations with real examples.

3. **Model comparison**

   * Compare Random Forest with gradient-boosting and lightweight deep-learning approaches.

4. **Defect localization**

   * Identify the image regions responsible for detected quality problems.

5. **Improved uncertainty estimation**

   * Calibrate model probabilities and investigate ambiguous predictions.

6. **Automated testing**

   * Add automated backend, frontend, and ML pipeline tests.

7. **Production deployment**

   * Deploy the containerized application to cloud infrastructure.

8. **Performance optimization**

   * Improve throughput for simultaneous image-analysis requests.

---

# 21. Technologies Used

### Frontend

* React
* Vite
* React Router
* Tailwind CSS
* DaisyUI

### Backend

* Python
* FastAPI
* OpenCV
* NumPy
* Pandas
* SQLAlchemy
* SQLite

### Machine Learning

* Scikit-learn
* Random Forest
* Joblib

### Development & Deployment

* Docker
* Docker Compose
* Git
* GitHub

---

# 22. Assessment Requirement Mapping

The implementation addresses the major requirements of the technical assessment:

| Assessment Requirement      | Implementation                                     |
| --------------------------- | -------------------------------------------------- |
| Blur detection              | Laplacian variance + ML classification             |
| Underexposure               | Bright-pixel/dark-pixel statistics + ML            |
| Overexposure                | Bright-pixel statistics + ML                       |
| Image noise                 | Noise residual feature + ML                        |
| Corruption                  | Synthetic corruption examples + ML                 |
| Potential defect            | Synthetic visual anomaly examples + ML             |
| AI-based decision component | Random Forest classifier                           |
| Computer vision features    | 16 engineered image-quality features               |
| REST API                    | FastAPI                                            |
| File validation             | Frontend + backend validation                      |
| Persistent results          | SQLite + SQLAlchemy                                |
| Analysis history            | `/api/analyses` + React history page               |
| Explainability              | Feature statistics + feature importance + severity |
| Evaluation                  | Accuracy, precision, recall, F1, confusion matrix  |
| Deployment                  | Docker + Docker Compose                            |
| Health check                | `/health`                                          |
| Environment configuration   | `VITE_API_URL`                                     |
| Model inference             | Serialized Joblib model loaded by backend          |

---

# 23. License

This project was developed as part of an internship technical assessment.
