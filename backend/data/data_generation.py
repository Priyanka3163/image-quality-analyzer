import os
import shutil
import random
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import kagglehub

DATASET_NAME = "phucthaiv02/butterfly-image-classification"
OUTPUT_DIR = Path(__file__).resolve().parent / "butterfly_quality_dataset"

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

MAX_TRAIN_IMAGES = 25
MAX_TEST_IMAGES = 5

# Download the source dataset from Kaggle
print("Downloading Kaggle dataset...")
dataset_path = Path(kagglehub.dataset_download(DATASET_NAME))
print(f"Dataset downloaded to:\n{dataset_path}")

print("\nDataset contents:")
for item in dataset_path.rglob("*"):
    if item.is_file():
        print(item.relative_to(dataset_path))

# Find the training and testing CSV files
csv_files = list(dataset_path.rglob("*.csv"))
print("\nCSV files found:")
for csv in csv_files:
    print(csv)

def find_csv(keyword):
    matches = [csv for csv in csv_files if keyword.lower() in csv.name.lower()]
    if not matches:
        raise FileNotFoundError(f"Could not find CSV containing '{keyword}'.")
    return matches[0]

train_csv = find_csv("train")
test_csv = find_csv("test")

print("\nTraining CSV:", train_csv)
print("Testing CSV:", test_csv)

train_df = pd.read_csv(train_csv)
test_df = pd.read_csv(test_csv)

print("\nTraining columns:")
print(train_df.columns.tolist())
print("\nTesting columns:")
print(test_df.columns.tolist())
print("\nTraining sample:")
print(train_df.head())

# Locate directories containing source images
image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def find_image_directories(root):
    directories = []
    for directory in root.rglob("*"):
        if not directory.is_dir():
            continue
        images = [file for file in directory.iterdir() if file.is_file() and file.suffix.lower() in image_extensions]
        if images:
            directories.append(directory)
    return directories

image_dirs = find_image_directories(dataset_path)

print("\nDirectories containing images:")
for directory in image_dirs:
    print(directory)

# Build a filename lookup for the source images
image_lookup = {}
for image_dir in image_dirs:
    for image_file in image_dir.iterdir():
        if image_file.is_file() and image_file.suffix.lower() in image_extensions:
            image_lookup[image_file.name] = image_file

print(f"\nFound {len(image_lookup)} unique image files.")

def find_image(image_name):
    if image_name in image_lookup:
        return image_lookup[image_name]
    basename = Path(str(image_name)).name
    if basename in image_lookup:
        return image_lookup[basename]
    raise FileNotFoundError(f"Could not locate image: {image_name}")

# Image-quality degradation functions
def apply_blur(image):
    kernel_size = random.choice([9, 11, 13, 15, 17, 19, 21])
    sigma = random.uniform(3.0, 7.0)
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigmaX=sigma)

def apply_underexposure(image):
    gamma = random.uniform(1.8, 2.8)
    normalized = image / 255.0
    darkened = np.power(normalized, gamma)
    return np.clip(darkened * 255, 0, 255).astype(np.uint8)

def apply_overexposure(image):
    gamma = random.uniform(0.35, 0.65)
    normalized = image / 255.0
    brightened = np.power(normalized, gamma)
    brightened *= random.uniform(1.05, 1.30)
    return np.clip(brightened * 255, 0, 255).astype(np.uint8)

def apply_gaussian_noise(image):
    sigma = random.uniform(35, 75)
    noise = np.random.normal(0, sigma, image.shape)
    noisy = image.astype(np.float32) + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)

def apply_salt_pepper_noise(image):
    noisy = image.copy()
    amount = random.uniform(0.01, 0.04)
    total_pixels = image.shape[0] * image.shape[1]
    num_pixels = int(total_pixels * amount)

    for _ in range(num_pixels // 2):
        y = random.randint(0, image.shape[0] - 1)
        x = random.randint(0, image.shape[1] - 1)
        noisy[y, x] = 255

    for _ in range(num_pixels // 2):
        y = random.randint(0, image.shape[0] - 1)
        x = random.randint(0, image.shape[1] - 1)
        noisy[y, x] = 0

    return noisy

def apply_corruption(image):
    corrupted = image.copy()
    h, w = corrupted.shape[:2]

    x1 = random.randint(0, max(0, w // 3))
    y1 = random.randint(0, max(0, h // 3))
    x2 = random.randint(max(x1 + 1, int(w * 0.5)), w)
    y2 = random.randint(max(y1 + 1, int(h * 0.5)), h)

    # Replace a large region with random pixels
    corrupted[y1:y2, x1:x2] = np.random.randint(0, 256, corrupted[y1:y2, x1:x2].shape, dtype=np.uint8)

    # Apply severe JPEG compression
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, 5]
    success, encoded = cv2.imencode(".jpg", corrupted, encode_params)

    if success:
        corrupted = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

    return corrupted

def apply_potential_defect(image):
    result = apply_blur(image)
    result = apply_gaussian_noise(result)
    return cv2.convertScaleAbs(result, alpha=1.8, beta=-80)

# Create fresh output directories
if OUTPUT_DIR.exists():
    print(f"\nRemoving existing output directory: {OUTPUT_DIR}")
    shutil.rmtree(OUTPUT_DIR)

train_output_dir = OUTPUT_DIR / "train"
test_output_dir = OUTPUT_DIR / "test"

train_output_dir.mkdir(parents=True, exist_ok=True)
test_output_dir.mkdir(parents=True, exist_ok=True)

# Generate degraded images and labels for one dataset split
def process_split(df, split_name, output_dir, max_images=None):
    print(f"\n==============================")
    print(f"Processing {split_name.upper()} set")
    print(f"==============================")

    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    if max_images is not None:
        df = df.head(max_images)

    generated_rows = []
    corruption_created = False
    defect_created = False

    for index, row in df.iterrows():
        possible_columns = ["filename", "file_name", "image", "image_name", "path", "filepath"]
        image_column = None

        for column in possible_columns:
            if column in df.columns:
                image_column = column
                break

        if image_column is None:
            raise ValueError(f"Could not determine image filename column. Available columns: {df.columns.tolist()}")

        image_name = str(row[image_column])
        image_path = find_image(image_name)
        image = cv2.imread(str(image_path))

        if image is None:
            print(f"WARNING: Could not read {image_path}")
            continue

        # Save the original acceptable image
        original_filename = f"{Path(image_name).stem}_original{Path(image_name).suffix}"
        cv2.imwrite(str(output_dir / original_filename), image)

        original_row = row.to_dict()
        original_row["filename"] = original_filename
        original_row["quality_label"] = "ACCEPTABLE"
        original_row["source_image"] = image_name
        generated_rows.append(original_row)

        # Generate blur
        random.seed(RANDOM_SEED + index)
        blurred = apply_blur(image)
        blur_filename = f"{Path(image_name).stem}_blur{Path(image_name).suffix}"
        cv2.imwrite(str(output_dir / blur_filename), blurred)

        blur_row = row.to_dict()
        blur_row["filename"] = blur_filename
        blur_row["quality_label"] = "BLUR"
        blur_row["source_image"] = image_name
        generated_rows.append(blur_row)

        # Generate underexposure
        random.seed(RANDOM_SEED + index + 10000)
        underexposed = apply_underexposure(image)
        under_filename = f"{Path(image_name).stem}_underexposed{Path(image_name).suffix}"
        cv2.imwrite(str(output_dir / under_filename), underexposed)

        under_row = row.to_dict()
        under_row["filename"] = under_filename
        under_row["quality_label"] = "UNDEREXPOSED"
        under_row["source_image"] = image_name
        generated_rows.append(under_row)

        # Generate overexposure
        random.seed(RANDOM_SEED + index + 20000)
        overexposed = apply_overexposure(image)
        over_filename = f"{Path(image_name).stem}_overexposed{Path(image_name).suffix}"
        cv2.imwrite(str(output_dir / over_filename), overexposed)

        over_row = row.to_dict()
        over_row["filename"] = over_filename
        over_row["quality_label"] = "OVEREXPOSED"
        over_row["source_image"] = image_name
        generated_rows.append(over_row)

        # Generate Gaussian noise
        random.seed(RANDOM_SEED + index + 30000)
        np.random.seed(RANDOM_SEED + index + 30000)
        noisy = apply_gaussian_noise(image)
        noise_filename = f"{Path(image_name).stem}_noise{Path(image_name).suffix}"
        cv2.imwrite(str(output_dir / noise_filename), noisy)

        noise_row = row.to_dict()
        noise_row["filename"] = noise_filename
        noise_row["quality_label"] = "NOISE"
        noise_row["source_image"] = image_name
        generated_rows.append(noise_row)

        # Generate one corruption sample
        if not corruption_created:
            random.seed(RANDOM_SEED + 40000)
            np.random.seed(RANDOM_SEED + 40000)
            corrupted = apply_corruption(image)
            corruption_filename = f"{Path(image_name).stem}_corrupted{Path(image_name).suffix}"
            cv2.imwrite(str(output_dir / corruption_filename), corrupted)

            corruption_row = row.to_dict()
            corruption_row["filename"] = corruption_filename
            corruption_row["quality_label"] = "CORRUPTED"
            corruption_row["source_image"] = image_name
            generated_rows.append(corruption_row)

        # Generate one potential defect sample
        if not defect_created:
            random.seed(RANDOM_SEED + 50000)
            np.random.seed(RANDOM_SEED + 50000)
            defective = apply_potential_defect(image)
            defect_filename = f"{Path(image_name).stem}_defect{Path(image_name).suffix}"
            cv2.imwrite(str(output_dir / defect_filename), defective)

            defect_row = row.to_dict()
            defect_row["filename"] = defect_filename
            defect_row["quality_label"] = "POTENTIAL_DEFECT"
            defect_row["source_image"] = image_name
            generated_rows.append(defect_row)

        if (index + 1) % 100 == 0:
            print(f"Processed {index + 1}/{len(df)} images")

    # Save labels for the generated images
    output_df = pd.DataFrame(generated_rows)
    output_csv = OUTPUT_DIR / f"{split_name}_quality.csv"
    output_df.to_csv(output_csv, index=False)

    print(f"\nSaved CSV: {output_csv}")
    print("\nQuality label distribution:")
    print(output_df["quality_label"].value_counts())

    return output_df

# Generate training data
train_quality_df = process_split(train_df, "train", train_output_dir, MAX_TRAIN_IMAGES)

# Generate test data
test_quality_df = process_split(test_df, "test", test_output_dir, MAX_TEST_IMAGES)

print("\n\n========================================")
print("DATASET GENERATION COMPLETE")
print("========================================")
print(f"\nOutput directory:\n{OUTPUT_DIR.resolve()}")

print("\nTraining distribution:")
print(train_quality_df["quality_label"].value_counts())

print("\nTesting distribution:")
print(test_quality_df["quality_label"].value_counts())

print("\nGenerated structure:")
print(f"""
{OUTPUT_DIR}/
│
├── train/
│   ├── image_original.jpg
│   ├── image_blur.jpg
│   ├── image_underexposed.jpg
│   ├── image_overexposed.jpg
│   ├── image_noise.jpg
│   ├── ...
│
├── test/
│   ├── ...
│
├── train_quality.csv
└── test_quality.csv
""")