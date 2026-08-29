# AI Image Quality Analyzer

An AI-powered web application that analyzes uploaded images and evaluates their visual quality using machine-learning-based image-quality features.

The application provides a complete end-to-end pipeline:

**Image Upload → Feature Extraction → Machine Learning Classification → Quality Assessment → Result Storage → Web Interface**

---

## Features

* Upload JPG, JPEG, PNG, and WebP images
* Client-side file validation

  * Supported image formats
  * Maximum file size of 10 MB
* Image preview before analysis
* Machine-learning-based image-quality classification
* Quality score and predicted quality category
* Issue severity and prediction confidence
* Image dimensions and extracted image statistics
* Analysis history stored in a database
* Dedicated history page
* REST API built with FastAPI
* React-based frontend
* Dockerized frontend and backend
* Dark-mode user interface

---

## Quality Categories

The current classifier supports seven image-quality categories:

| Category           | Description                                             |
| ------------------ | ------------------------------------------------------- |
| `ACCEPTABLE`       | Image has generally acceptable visual quality           |
| `BLUR`             | Image contains significant loss of sharpness            |
| `UNDEREXPOSED`     | Image is excessively dark                               |
| `OVEREXPOSED`      | Image contains excessive brightness or clipping         |
| `NOISE`            | Image contains significant image noise                  |
| `CORRUPTED`        | Image contains severe visual corruption                 |
| `POTENTIAL_DEFECT` | Image contains a potentially problematic visual anomaly |

---

## System Architecture

```text
                         ┌──────────────────────┐
                         │      React UI         │
                         │                      │
                         │  Image Upload        │
                         │  Preview             │
                         │  Analysis Results    │
                         │  History             │
                         └──────────┬───────────┘
                                    │
                              HTTP / REST API
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │      Backend         │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ Image Validation     │
                         │ & OpenCV Decoding    │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ Feature Extraction   │
                         │                      │
                         │ Brightness           │
                         │ Contrast             │
                         │ Sharpness            │
                         │ Edge Density         │
                         │ Noise                │
                         │ Saturation            │
                         │ Texture              │
                         │ Entropy              │
                         │ Regional Statistics  │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ Random Forest Model  │
                         │                      │
                         │ quality_model.joblib │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ Prediction +         │
                         │ Confidence +         │
                         │ Quality Assessment   │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ SQLite Database      │
                         │ Analysis History     │
                         └──────────────────────┘
```

---

## Machine Learning Pipeline

The machine-learning component uses interpretable image-quality features rather than directly classifying raw image pixels.

### Feature Extraction

The feature extractor calculates 16 image-quality features, including:

* Mean brightness
* Brightness variation
* Dark pixel ratio
* Bright pixel ratio
* Dynamic range
* Laplacian variance for sharpness
* Edge density
* Noise estimate
* Mean and standard deviation of saturation
* High-saturation pixel ratio
* Local texture statistics
* Image entropy
* Regional mean variation
* Regional standard-deviation variation

These features are passed to a **Random Forest classifier**.

### Model

The current model uses:

```text
RandomForestClassifier
n_estimators = 300
class_weight = balanced
random_state = 42
```

The trained model is serialized using `joblib` and stored at:

```text
backend/ml/quality_model.joblib
```

---

## Dataset Generation

The project uses the publicly available butterfly image dataset as a source of clean images.

Synthetic image-quality variations are generated from the source images to create examples for the different quality categories.

The data-generation pipeline currently includes:

* Original / acceptable images
* Gaussian blur
* Underexposure
* Overexposure
* Gaussian noise
* Image corruption
* Potential visual defects

The generation script is located at:

```text
backend/data/data_generation.py
```

The generated dataset is intentionally separated from the application code and does not need to be included in the deployed application.

---

## Model Evaluation

The Random Forest model was evaluated using a held-out test split.

The current development model achieved approximately:

**91.4% test accuracy**

The repository also includes evaluation code for:

* Accuracy
* Classification report
* Confusion matrix
* Feature importance

The current dataset used during development is intentionally smaller than the full source dataset so that the complete training and experimentation pipeline could be developed efficiently.

For a production-quality model, the next step would be to generate and train on a substantially larger dataset with more diverse real-world examples.

---

## Backend API

The backend is implemented using **FastAPI**.

### Health Check

```http
GET /health
```

Returns:

```json
{
  "status": "healthy"
}
```

### Analyze Image

```http
POST /api/analyze
```

Accepts an image using multipart form data.

The API:

1. Validates the uploaded file type
2. Reads the image
3. Decodes the image using OpenCV
4. Rejects unreadable or invalid images
5. Extracts image-quality features
6. Runs the Random Forest model
7. Calculates prediction confidence
8. Determines issue severity
9. Calculates an overall quality score
10. Stores the analysis in the database
11. Returns the analysis result as JSON

### Analysis History

```http
GET /api/analyses
```

Returns previously stored image analyses ordered by creation time.

Interactive API documentation is available through FastAPI at:

```text
http://localhost:8000/docs
```

---

## Frontend

The frontend is built using:

* React
* Vite
* React Router
* Tailwind CSS
* DaisyUI

The application contains:

### Home

Allows the user to:

1. Select an image
2. Preview the image
3. Start analysis
4. View an analysis progress state
5. View the final quality assessment

### History

Displays previous image analyses stored by the backend.

Each history entry includes information such as:

* Filename
* Quality score
* Quality classification
* Confidence
* Severity
* Analysis timestamp

---

## Project Structure

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

---

## Running the Application with Docker

### Prerequisites

Install:

* Docker
* Docker Compose

### Start the application

From the project root:

```bash
docker compose up --build
```

Or run it in detached mode:

```bash
docker compose up --build -d
```

The application consists of separate frontend and backend containers.

### Frontend

```text
http://localhost:5173
```

### Backend API

```text
http://localhost:8000
```

### FastAPI Documentation

```text
http://localhost:8000/docs
```

### Stop the application

```bash
docker compose down
```

---

## Environment Configuration

The frontend uses an environment variable for the backend API URL.

Create a `.env` file in the frontend directory based on:

```text
frontend/.env.example
```

Example:

```env
VITE_API_URL=http://localhost:8000
```

Environment files containing local configuration should not be committed to the repository.

---

## Error Handling

The application includes validation and error handling at both the frontend and backend levels.

Examples include:

* Unsupported file format
* Files larger than 10 MB
* Empty uploads
* Invalid or unreadable image files
* Backend/API connection failures
* Repeated analysis clicks while an analysis is already running

The frontend disables repeated analysis while a request is being processed and displays an appropriate error message when analysis fails.

---

## Current Limitations

This project is currently a prototype / assessment implementation.

The machine-learning model was trained using a relatively small generated dataset during development. The source dataset is substantially larger, but processing the full dataset was outside the practical development timeframe.

The synthetic degradation functions are also simplified representations of image-quality problems. In particular, the `POTENTIAL_DEFECT` and `CORRUPTED` categories are currently generated synthetically and should be expanded with more representative real-world examples for a production system.

Future improvements could include:

* Training on the complete source dataset
* Increasing the diversity of degradation parameters
* Adding real-world defective images
* Hyperparameter optimization
* More robust defect localization
* Additional image-quality features
* Model versioning
* Authentication and user-specific analysis history
* Cloud deployment
* Automated testing and CI/CD

---

## Future Improvements

Potential extensions include:

1. **Larger training dataset**

   Train using substantially more source images and generated variations.

2. **Real-world defect data**

   Replace or supplement synthetic defect examples with real image-quality failure cases.

3. **Model improvements**

   Compare the Random Forest approach against alternative machine-learning and deep-learning architectures.

4. **Defect localization**

   Extend the system from image-level classification to identifying where a quality issue occurs in an image.

5. **Production deployment**

   Deploy the frontend and backend using cloud infrastructure and configure a production database.

6. **Automated testing**

   Add automated API, frontend, and ML pipeline tests.

---

## Technologies Used

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

## License

This project was developed as part of an internship / technical assessment.
