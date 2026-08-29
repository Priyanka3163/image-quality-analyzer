import cv2
import numpy as np


def calculate_entropy(gray):
    # Calculate grayscale image entropy
    histogram = cv2.calcHist([gray], [0], None, [256], [0, 256])
    histogram = histogram.flatten()
    histogram = histogram / (histogram.sum() + 1e-8)
    entropy = -np.sum(histogram * np.log2(histogram + 1e-8))
    return float(entropy)


def extract_features(image):
    # Validate and prepare image
    if image is None:
        raise ValueError("Invalid image")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray_float = gray.astype(np.float32)

    # Calculate brightness statistics
    brightness_mean = np.mean(gray_float)
    brightness_std = np.std(gray_float)
    dark_pixel_ratio = np.mean(gray < 30)
    bright_pixel_ratio = np.mean(gray > 225)

    # Calculate contrast
    p5 = np.percentile(gray_float, 5)
    p95 = np.percentile(gray_float, 95)
    dynamic_range = p95 - p5

    # Estimate image sharpness
    laplacian = cv2.Laplacian(gray_float, cv2.CV_32F)
    laplacian_variance = np.var(laplacian)

    # Calculate edge density
    edges = cv2.Canny(gray, threshold1=100, threshold2=200)
    edge_density = np.mean(edges > 0)

    # Estimate image noise
    blurred = cv2.GaussianBlur(gray_float, (3, 3), 0)
    noise_residual = gray_float - blurred
    noise_estimate = np.std(noise_residual)

    # Calculate saturation statistics
    saturation = hsv[:, :, 1].astype(np.float32)
    saturation_mean = np.mean(saturation)
    saturation_std = np.std(saturation)
    high_saturation_ratio = np.mean(saturation > 220)

    # Calculate local texture statistics
    gray_float = gray.astype(np.float32)
    local_mean = cv2.GaussianBlur(gray_float, (7, 7), 0)
    local_sq_mean = cv2.GaussianBlur(gray_float * gray_float, (7, 7), 0)
    local_variance = local_sq_mean - local_mean ** 2
    local_variance = np.maximum(local_variance, 0)
    texture_mean = np.mean(local_variance)
    texture_std = np.std(local_variance)

    # Calculate image entropy
    entropy = calculate_entropy(gray)

    # Calculate regional statistics
    height, width = gray.shape
    regions = [
        gray[:height // 2, :width // 2],
        gray[:height // 2, width // 2:],
        gray[height // 2:, :width // 2],
        gray[height // 2:, width // 2:]
    ]

    regional_means = [np.mean(region) for region in regions]
    regional_stds = [np.std(region) for region in regions]
    regional_mean_variation = np.std(regional_means)
    regional_std_variation = np.std(regional_stds)

    # Build final feature vector
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

    return np.array(features, dtype=np.float32)


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