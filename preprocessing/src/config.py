import os

DATA_DIR = "../data"
CONTROL_DIR = f"{DATA_DIR}/control"
TEST_DIR = f"{DATA_DIR}/cardiac"

MIN_LENGTH_SEG = 180  # Desired duration for truncated files in seconds
POLICY = "early"  # "early", "late", "best"

CLIP_START_LENGTH = 10  # Number of RR entries to clip from the beginning of the data

QUALITY_THRESHOLD = 0.0  # Data quality threshold

# THRESHOLDS IN MILLISECONDS
LOW_RRI = 300
HIGH_RRI = 2000

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Output directories
OUTPUT_DIR = os.path.join(BASE_DIR, f"{DATA_DIR}/output")
DENOISED_OUTPUT_DIR = os.path.join(BASE_DIR, f"{DATA_DIR}/output/denoised")
TRUNCATED_OUTPUT_DIR = os.path.join(
    BASE_DIR, f"{DATA_DIR}/output/truncated_{round(MIN_LENGTH_SEG/60, 1)}min_{POLICY}"
)

# Processing parameters
OUTLIER_THRESHOLD = 3
MEDIAN_FILTER_KERNEL_SIZE = 5

# Logging configuration
LOG_FILE = os.path.join(BASE_DIR, f"{DATA_DIR}/logs/rr_processing.log")
LOG_LEVEL = "ERROR"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

control_basename = os.path.basename(CONTROL_DIR)
test_basename = os.path.basename(TEST_DIR)

# Create directories if they do not exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(DENOISED_OUTPUT_DIR, control_basename), exist_ok=True)
os.makedirs(os.path.join(DENOISED_OUTPUT_DIR, test_basename), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)