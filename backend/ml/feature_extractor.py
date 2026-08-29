import cv2
import numpy as np


def calculate_entropy(gray):
    """
    Calculate grayscale image entropy.
    Higher entropy generally indicates more information/complexity.
    """
    histogram = cv2.calcHist(
        [gray],
        [0],
        None,
        [256],
        [0, 256]
    )

    histogram = histogram.flatten()
    histogram = histogram / (histogram.sum() + 1e-8)

    entropy = -np.sum(
        histogram * np.log2(histogram + 1e-8)
    )

    return float(entropy)


def extract_features(image):
    """
    Extract interpretable image-quality features.

    Returns:
        numpy array containing the feature vector.
    """

    # --------------------------------------------------
    # Basic validation
    # --------------------------------------------------

    if image is None:
        raise ValueError("Invalid image")

    # --------------------------------------------------
    # Convert image representations
    # --------------------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    gray_float = gray.astype(np.float32)


    # --------------------------------------------------
    # 1. Brightness
    # --------------------------------------------------

    brightness_mean = np.mean(gray_float)
    brightness_std = np.std(gray_float)

    # Very dark pixels
    dark_pixel_ratio = np.mean(gray < 30)

    # Very bright pixels
    bright_pixel_ratio = np.mean(gray > 225)

    # --------------------------------------------------
    # 2. Contrast
    # --------------------------------------------------

    p5 = np.percentile(gray_float, 5)
    p95 = np.percentile(gray_float, 95)

    dynamic_range = p95 - p5

    # --------------------------------------------------
    # 3. Sharpness
    # --------------------------------------------------

    laplacian = cv2.Laplacian(
            gray_float,
            cv2.CV_32F
        )

    laplacian_variance = np.var(laplacian)

    # --------------------------------------------------
    # 4. Edge density
    # --------------------------------------------------

    edges = cv2.Canny(
        gray,
        threshold1=100,
        threshold2=200
    )

    edge_density = np.mean(edges > 0)

    # --------------------------------------------------
    # 5. Noise estimation
    #
    # Compare original image with a lightly
    # Gaussian-smoothed image.
    # --------------------------------------------------

    blurred = cv2.GaussianBlur(
        gray_float,
        (3, 3),
        0
    )

    noise_residual = gray_float - blurred

    noise_estimate = np.std(
        noise_residual
    )

    # --------------------------------------------------
    # 6. Saturation
    # --------------------------------------------------

    saturation = hsv[:, :, 1].astype(
        np.float32
    )

    saturation_mean = np.mean(saturation)
    saturation_std = np.std(saturation)

    high_saturation_ratio = np.mean(
        saturation > 220
    )

    # --------------------------------------------------
    # 7. Texture / local variance
    # --------------------------------------------------

    gray_float = gray.astype(np.float32)

    local_mean = cv2.GaussianBlur(
        gray_float,
        (7, 7),
        0
    )

    local_sq_mean = cv2.GaussianBlur(
        gray_float * gray_float,
        (7, 7),
        0
    )

    local_variance = (
        local_sq_mean -
        local_mean ** 2
    )

    local_variance = np.maximum(
        local_variance,
        0
    )

    texture_mean = np.mean(
        local_variance
    )

    texture_std = np.std(
        local_variance
    )

    # --------------------------------------------------
    # 8. Entropy
    # --------------------------------------------------

    entropy = calculate_entropy(gray)

    # --------------------------------------------------
    # 9. Regional statistics
    #
    # Helps identify localized defects.
    # --------------------------------------------------

    height, width = gray.shape

    regions = [
        gray[:height // 2, :width // 2],
        gray[:height // 2, width // 2:],
        gray[height // 2:, :width // 2],
        gray[height // 2:, width // 2:]
    ]

    regional_means = [
        np.mean(region)
        for region in regions
    ]

    regional_stds = [
        np.std(region)
        for region in regions
    ]

    regional_mean_variation = np.std(
        regional_means
    )

    regional_std_variation = np.std(
        regional_stds
    )

    # --------------------------------------------------
    # Final feature vector
    # --------------------------------------------------

    features = [
        brightness_mean,
        brightness_std,

        dark_pixel_ratio,
        bright_pixel_ratio,

        dynamic_range,

        laplacian_variance,

        edge_density,

        noise_estimate,

        saturation_mean,
        saturation_std,
        high_saturation_ratio,

        texture_mean,
        texture_std,

        entropy,

        regional_mean_variation,
        regional_std_variation
    ]

    return np.array(
        features,
        dtype=np.float32
    )


FEATURE_NAMES = [
    "brightness_mean",
    "brightness_std",

    "dark_pixel_ratio",
    "bright_pixel_ratio",

    "dynamic_range",

    "laplacian_variance",

    "edge_density",

    "noise_estimate",

    "saturation_mean",
    "saturation_std",
    "high_saturation_ratio",

    "texture_mean",
    "texture_std",

    "entropy",

    "regional_mean_variation",
    "regional_std_variation"
]