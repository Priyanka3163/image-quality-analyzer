import os
from pathlib import Path
import joblib
import pandas as pd
import cv2
from feature_extractor import extract_features, FEATURE_NAMES

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)


BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)
# =====================================================
# Configuration
# =====================================================

TRAIN_CSV = BASE_DIR / "data" / "butterfly_quality_dataset" / "train_quality.csv"
TEST_CSV = BASE_DIR / "data" / "butterfly_quality_dataset" / "test_quality.csv"

TRAIN_IMAGE_DIR = BASE_DIR / "data" / "butterfly_quality_dataset" / "train"
TEST_IMAGE_DIR = BASE_DIR / "data" / "butterfly_quality_dataset" / "test"

MODEL_OUTPUT = "quality_model.joblib"


# =====================================================
# Load dataset
# =====================================================

def load_dataset(csv_path, image_root):

    df = pd.read_csv(csv_path)

    features = []
    labels = []

    failed_images = []

    for _, row in df.iterrows():

        filename = row["filename"]
        label = row["quality_label"]

        image_path = os.path.join(
            image_root,
            filename
        )

        # -------------------------------------------------
        # If images are nested inside source-image folders,
        # search recursively.
        # -------------------------------------------------

        if not os.path.exists(image_path):

            found_path = None

            for root, _, files in os.walk(image_root):

                if filename in files:

                    found_path = os.path.join(
                        root,
                        filename
                    )

                    break

            image_path = found_path

        # -------------------------------------------------
        # Validate path
        # -------------------------------------------------

        if image_path is None or not os.path.exists(image_path):

            failed_images.append(
                (filename, "File not found")
            )

            continue

        # -------------------------------------------------
        # Read image
        # -------------------------------------------------

        image = cv2.imread(image_path)

        if image is None:

            failed_images.append(
                (filename, "Unreadable image")
            )

            continue

        # -------------------------------------------------
        # Extract features
        # -------------------------------------------------

        try:

            image_features = extract_features(
                image
            )

            features.append(
                image_features
            )

            labels.append(
                label
            )

        except Exception as error:

            failed_images.append(
                (filename, str(error))
            )

    print(
        f"Successfully loaded: {len(features)} images"
    )

    if failed_images:

        print(
            f"Failed images: {len(failed_images)}"
        )

        for item in failed_images[:10]:

            print(item)

    return features, labels


# =====================================================
# Main training
# =====================================================

def main():

    print("\nLoading training data...")

    X_train, y_train = load_dataset(
        TRAIN_CSV,
        TRAIN_IMAGE_DIR
    )

    print("\nLoading test data...")

    X_test, y_test = load_dataset(
        TEST_CSV,
        TEST_IMAGE_DIR
    )

    print("\nDataset summary")

    print(
        f"Training samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    # --------------------------------------------------
    # Convert to arrays
    # --------------------------------------------------

    import numpy as np

    X_train = np.array(X_train)
    X_test = np.array(X_test)

    # --------------------------------------------------
    # Train Random Forest
    # --------------------------------------------------

    print("\nTraining Random Forest...")

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------
    # Evaluation
    # --------------------------------------------------

    print("\nEvaluating model...")

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(
        f"\nAccuracy: {accuracy:.4f}"
    )

    print("\nClassification Report")

    print(
        classification_report(
            y_test,
            predictions,
            digits=4
        )
    )

    print("\nConfusion Matrix")

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    # --------------------------------------------------
    # Feature importance
    # --------------------------------------------------

    print("\nFeature Importance")

    importance = model.feature_importances_

    feature_importance = sorted(
        zip(
            FEATURE_NAMES,
            importance
        ),
        key=lambda x: x[1],
        reverse=True
    )

    for feature, score in feature_importance:

        print(
            f"{feature:<30} {score:.4f}"
        )

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    model_data = {
        "model": model,
        "feature_names": FEATURE_NAMES
    }

    joblib.dump(
        model_data,
        MODEL_OUTPUT
    )

    print(
        f"\nModel saved to: {MODEL_OUTPUT}"
    )


if __name__ == "__main__":
    main()