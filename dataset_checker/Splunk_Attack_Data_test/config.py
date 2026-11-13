"""Configuration for the Splunk Attack Data audit."""
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_verified")
SPLUNK_ATTACK_DATA_REPO = "https://github.com/splunk/attack_data.git"
TECHNIQUE_ID_PATTERN = r"T\d{4}(?:\.\d{3})?"
LONG_SEQUENCE_THRESHOLD = 16
SESSION_GAP_SECONDS = 30 * 60
SESSION_MAX_DURATION_SECONDS = 4 * 60 * 60
