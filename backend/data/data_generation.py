import os
import shutil
import random
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import kagglehub


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_NAME = "phucthaiv02/butterfly-image-classification"

# Where the generated dataset will be created
OUTPUT_DIR = Path("butterfly_quality_dataset")

# Reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Number of source images to use from each split.
# Set to None to use ALL images.
MAX_TRAIN_IMAGES = 25
MAX_TEST_IMAGES = 5


# ============================================================
# 1. DOWNLOAD DATASET FROM KAGGLE
# ============================================================

print("Downloading Kaggle dataset...")

dataset_path = Path(
    kagglehub.dataset_download(DATASET_NAME)
)

print(f"Dataset downloaded to:\n{dataset_path}")


# ============================================================
# 2. INSPECT DATASET STRUCTURE
# ============================================================

print("\nDataset contents:")

for item in dataset_path.rglob("*"):
    if item.is_file():
        print(item.relative_to(dataset_path))


# ============================================================
# 3. FIND CSV FILES
# ============================================================

csv_files = list(dataset_path.rglob("*.csv"))

print("\nCSV files found:")

for csv in csv_files:
    print(csv)


def find_csv(keyword):
    """
    Find a CSV whose filename contains keyword.
    """
    matches = [
        csv for csv in csv_files
        if keyword.lower() in csv.name.lower()
    ]

    if not matches:
        raise FileNotFoundError(
            f"Could not find CSV containing '{keyword}'."
        )

    return matches[0]


train_csv = find_csv("train")
test_csv = find_csv("test")

print("\nTraining CSV:", train_csv)
print("Testing CSV:", test_csv)


# ============================================================
# 4. READ CSVs
# ============================================================

train_df = pd.read_csv(train_csv)
test_df = pd.read_csv(test_csv)

print("\nTraining columns:")
print(train_df.columns.tolist())

print("\nTesting columns:")
print(test_df.columns.tolist())

print("\nTraining sample:")
print(train_df.head())


# ============================================================
# 5. FIND IMAGE DIRECTORIES
# ============================================================

image_extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


def find_image_directories(root):
    """
    Find directories containing image files.
    """
    directories = []

    for directory in root.rglob("*"):
        if not directory.is_dir():
            continue

        images = [
            file for file in directory.iterdir()
            if file.is_file()
            and file.suffix.lower() in image_extensions
        ]

        if images:
            directories.append(directory)

    return directories


image_dirs = find_image_directories(dataset_path)

print("\nDirectories containing images:")

for directory in image_dirs:
    print(directory)


# ============================================================
# 6. IMAGE LOOKUP
# ============================================================

# Create a lookup table so that a CSV image filename can
# be resolved regardless of which directory it is in.

image_lookup = {}

for image_dir in image_dirs:

    for image_file in image_dir.iterdir():

        if image_file.is_file() and image_file.suffix.lower() in image_extensions:

            # Store both the filename and filename without path
            image_lookup[image_file.name] = image_file


print(
    f"\nFound {len(image_lookup)} unique image files."
)


def find_image(image_name):
    """
    Locate an image using the filename stored in the CSV.
    """

    # Exact filename
    if image_name in image_lookup:
        return image_lookup[image_name]

    # Sometimes CSV contains a path rather than just filename
    basename = Path(str(image_name)).name

    if basename in image_lookup:
        return image_lookup[basename]

    raise FileNotFoundError(
        f"Could not locate image: {image_name}"
    )


# ============================================================
# 7. IMAGE DEGRADATION FUNCTIONS
# ============================================================

def apply_blur(image):
    """
    Apply significant Gaussian blur.

    Randomized severity:
        kernel: 9, 11, 13, ..., 21
        sigma:  3.0 - 7.0

    This intentionally produces clearly visible blur.
    """

    kernel_size = random.choice(
        [9, 11, 13, 15, 17, 19, 21]
    )

    sigma = random.uniform(3.0, 7.0)

    blurred = cv2.GaussianBlur(
        image,
        (kernel_size, kernel_size),
        sigmaX=sigma
    )

    return blurred


def apply_underexposure(image):
    """
    Darken the image using random gamma correction.

    gamma > 1 makes the image darker.
    """

    gamma = random.uniform(1.8, 2.8)

    normalized = image / 255.0

    darkened = np.power(
        normalized,
        gamma
    )

    darkened = np.clip(
        darkened * 255,
        0,
        255
    ).astype(np.uint8)

    return darkened


def apply_overexposure(image):
    """
    Brighten the image using gamma correction and
    intensity scaling.

    gamma < 1 makes the image brighter.
    """

    gamma = random.uniform(0.35, 0.65)

    normalized = image / 255.0

    brightened = np.power(
        normalized,
        gamma
    )

    # Additional scaling creates realistic clipping
    scale = random.uniform(1.05, 1.30)

    brightened *= scale

    brightened = np.clip(
        brightened * 255,
        0,
        255
    ).astype(np.uint8)

    return brightened


def apply_gaussian_noise(image):
    """
    Add Gaussian sensor-like noise.

    Noise strength is randomized so that all noisy images
    are not identical.
    """

    sigma = random.uniform(35,75)

    noise = np.random.normal(
        0,
        sigma,
        image.shape
    )

    noisy = image.astype(np.float32) + noise

    noisy = np.clip(
        noisy,
        0,
        255
    ).astype(np.uint8)

    return noisy


def apply_salt_pepper_noise(image):
    """
    Optional alternative noise generator.

    Randomly adds black and white pixels.
    """

    noisy = image.copy()

    amount = random.uniform(0.01, 0.04)

    total_pixels = image.shape[0] * image.shape[1]

    num_pixels = int(
        total_pixels * amount
    )

    # Salt
    for _ in range(num_pixels // 2):

        y = random.randint(
            0,
            image.shape[0] - 1
        )

        x = random.randint(
            0,
            image.shape[1] - 1
        )

        noisy[y, x] = 255

    # Pepper
    for _ in range(num_pixels // 2):

        y = random.randint(
            0,
            image.shape[0] - 1
        )

        x = random.randint(
            0,
            image.shape[1] - 1
        )

        noisy[y, x] = 0

    return noisy


def apply_corruption(image):
    """
    Create ONE severely degraded/corrupted image.

    This is intentionally aggressive so we can inspect
    whether this definition is appropriate before generating
    thousands of these.
    """

    corrupted = image.copy()

    h, w = corrupted.shape[:2]

    # Random rectangular region
    x1 = random.randint(0, max(0, w // 3))
    y1 = random.randint(0, max(0, h // 3))

    x2 = random.randint(
        max(x1 + 1, int(w * 0.5)),
        w
    )

    y2 = random.randint(
        max(y1 + 1, int(h * 0.5)),
        h
    )

    # Replace a large region with random pixels
    corrupted[y1:y2, x1:x2] = np.random.randint(
        0,
        256,
        corrupted[y1:y2, x1:x2].shape,
        dtype=np.uint8
    )

    # Also heavily compress it
    encode_params = [
        cv2.IMWRITE_JPEG_QUALITY,
        5
    ]

    success, encoded = cv2.imencode(
        ".jpg",
        corrupted,
        encode_params
    )

    if success:
        corrupted = cv2.imdecode(
            encoded,
            cv2.IMREAD_COLOR
        )

    return corrupted


def apply_potential_defect(image):
    """
    ONE intentionally severe visual anomaly.

    We combine multiple quality problems:
        - strong blur
        - strong noise
        - exposure distortion

    This is NOT intended to represent a real-world
    defect model yet. It is just a placeholder sample
    for inspection.
    """

    result = apply_blur(image)

    result = apply_gaussian_noise(result)

    # Strong brightness distortion
    result = cv2.convertScaleAbs(
        result,
        alpha=1.8,
        beta=-80
    )

    return result


# ============================================================
# 8. OUTPUT DIRECTORIES
# ============================================================

if OUTPUT_DIR.exists():

    print(
        f"\nRemoving existing output directory: {OUTPUT_DIR}"
    )

    shutil.rmtree(OUTPUT_DIR)


train_output_dir = OUTPUT_DIR / "train"
test_output_dir = OUTPUT_DIR / "test"

train_output_dir.mkdir(
    parents=True,
    exist_ok=True
)

test_output_dir.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 9. PROCESS A SPLIT
# ============================================================

def process_split(
    df,
    split_name,
    output_dir,
    max_images=None
):

    print(
        f"\n=============================="
    )

    print(
        f"Processing {split_name.upper()} set"
    )

    print(
        f"=============================="
    )

    # Shuffle so the selected images aren't dependent
    # on the ordering of the original CSV.
    df = df.sample(
        frac=1,
        random_state=RANDOM_SEED
    ).reset_index(drop=True)

    if max_images is not None:
        df = df.head(max_images)

    generated_rows = []

    corruption_created = False
    defect_created = False

    for index, row in df.iterrows():

        # ----------------------------------------------------
        # Get image filename
        # ----------------------------------------------------

        # Try common column names
        possible_columns = [
            "filename",
            "file_name",
            "image",
            "image_name",
            "path",
            "filepath"
        ]

        image_column = None

        for column in possible_columns:

            if column in df.columns:
                image_column = column
                break

        if image_column is None:

            raise ValueError(
                "Could not determine image filename column. "
                f"Available columns: {df.columns.tolist()}"
            )

        image_name = str(
            row[image_column]
        )

        image_path = find_image(image_name)

        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            print(
                f"WARNING: Could not read {image_path}"
            )

            continue

        # ----------------------------------------------------
        # Original image
        # ----------------------------------------------------

        original_filename = (
            f"{Path(image_name).stem}_original"
            f"{Path(image_name).suffix}"
        )

        original_output_path = (
            output_dir / original_filename
        )

        cv2.imwrite(
            str(original_output_path),
            image
        )

        original_row = row.to_dict()

        original_row["filename"] = original_filename
        original_row["quality_label"] = "ACCEPTABLE"
        original_row["source_image"] = image_name

        generated_rows.append(
            original_row
        )

        # ----------------------------------------------------
        # BLUR
        # ----------------------------------------------------

        random.seed(RANDOM_SEED + index)

        blurred = apply_blur(image)

        blur_filename = (
            f"{Path(image_name).stem}_blur"
            f"{Path(image_name).suffix}"
        )

        cv2.imwrite(
            str(output_dir / blur_filename),
            blurred
        )

        blur_row = row.to_dict()

        blur_row["filename"] = blur_filename
        blur_row["quality_label"] = "BLUR"
        blur_row["source_image"] = image_name

        generated_rows.append(
            blur_row
        )

        # ----------------------------------------------------
        # UNDEREXPOSURE
        # ----------------------------------------------------

        random.seed(RANDOM_SEED + index + 10000)

        underexposed = apply_underexposure(image)

        under_filename = (
            f"{Path(image_name).stem}_underexposed"
            f"{Path(image_name).suffix}"
        )

        cv2.imwrite(
            str(output_dir / under_filename),
            underexposed
        )

        under_row = row.to_dict()

        under_row["filename"] = under_filename
        under_row["quality_label"] = "UNDEREXPOSED"
        under_row["source_image"] = image_name

        generated_rows.append(
            under_row
        )

        # ----------------------------------------------------
        # OVEREXPOSURE
        # ----------------------------------------------------

        random.seed(RANDOM_SEED + index + 20000)

        overexposed = apply_overexposure(image)

        over_filename = (
            f"{Path(image_name).stem}_overexposed"
            f"{Path(image_name).suffix}"
        )

        cv2.imwrite(
            str(output_dir / over_filename),
            overexposed
        )

        over_row = row.to_dict()

        over_row["filename"] = over_filename
        over_row["quality_label"] = "OVEREXPOSED"
        over_row["source_image"] = image_name

        generated_rows.append(
            over_row
        )

        # ----------------------------------------------------
        # NOISE
        # ----------------------------------------------------

        random.seed(RANDOM_SEED + index + 30000)
        np.random.seed(RANDOM_SEED + index + 30000)

        noisy = apply_gaussian_noise(image)

        noise_filename = (
            f"{Path(image_name).stem}_noise"
            f"{Path(image_name).suffix}"
        )

        cv2.imwrite(
            str(output_dir / noise_filename),
            noisy
        )

        noise_row = row.to_dict()

        noise_row["filename"] = noise_filename
        noise_row["quality_label"] = "NOISE"
        noise_row["source_image"] = image_name

        generated_rows.append(
            noise_row
        )

        # ----------------------------------------------------
        # CORRUPTION
        # ----------------------------------------------------

        if not corruption_created:

            random.seed(RANDOM_SEED + 40000)

            np.random.seed(RANDOM_SEED + 40000)

            corrupted = apply_corruption(image)

            corruption_filename = (
                f"{Path(image_name).stem}_corrupted"
                f"{Path(image_name).suffix}"
            )

            cv2.imwrite(
                str(
                    output_dir / corruption_filename
                ),
                corrupted
            )

            corruption_row = row.to_dict()

            corruption_row["filename"] = (
                corruption_filename
            )

            corruption_row["quality_label"] = (
                "CORRUPTED"
            )

            corruption_row["source_image"] = (
                image_name
            )

            generated_rows.append(
                corruption_row
            )

            # corruption_created = True

            # print(
            #     f"\nCreated ONE corruption sample: "
            #     f"{corruption_filename}"
            # )

        # ----------------------------------------------------
        # POTENTIAL VISUAL DEFECT
        # ----------------------------------------------------

        if not defect_created:

            random.seed(RANDOM_SEED + 50000)

            np.random.seed(RANDOM_SEED + 50000)

            defective = apply_potential_defect(image)

            defect_filename = (
                f"{Path(image_name).stem}_defect"
                f"{Path(image_name).suffix}"
            )

            cv2.imwrite(
                str(
                    output_dir / defect_filename
                ),
                defective
            )

            defect_row = row.to_dict()

            defect_row["filename"] = (
                defect_filename
            )

            defect_row["quality_label"] = (
                "POTENTIAL_DEFECT"
            )

            defect_row["source_image"] = (
                image_name
            )

            generated_rows.append(
                defect_row
            )

            # defect_created = True

            # print(
            #     f"Created ONE potential defect sample: "
            #     f"{defect_filename}"
            # )

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        if (index + 1) % 100 == 0:

            print(
                f"Processed {index + 1}/{len(df)} images"
            )

    # --------------------------------------------------------
    # SAVE GENERATED CSV
    # --------------------------------------------------------

    output_df = pd.DataFrame(
        generated_rows
    )

    output_csv = (
        OUTPUT_DIR /
        f"{split_name}_quality.csv"
    )

    output_df.to_csv(
        output_csv,
        index=False
    )

    print(
        f"\nSaved CSV: {output_csv}"
    )

    print(
        "\nQuality label distribution:"
    )

    print(
        output_df["quality_label"]
        .value_counts()
    )

    return output_df


# ============================================================
# 10. GENERATE TRAINING DATA
# ============================================================

train_quality_df = process_split(
    train_df,
    "train",
    train_output_dir,
    MAX_TRAIN_IMAGES
)


# ============================================================
# 11. GENERATE TEST DATA
# ============================================================

test_quality_df = process_split(
    test_df,
    "test",
    test_output_dir,
    MAX_TEST_IMAGES
)


# ============================================================
# 12. FINAL SUMMARY
# ============================================================

print("\n\n========================================")
print("DATASET GENERATION COMPLETE")
print("========================================")

print(
    f"\nOutput directory:\n{OUTPUT_DIR.resolve()}"
)

print("\nTraining distribution:")
print(
    train_quality_df["quality_label"]
    .value_counts()
)

print("\nTesting distribution:")
print(
    test_quality_df["quality_label"]
    .value_counts()
)

print("\nGenerated structure:")

print(
    f"""
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
"""
)
