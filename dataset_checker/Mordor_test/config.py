"""Local Mordor metadata audit configuration."""
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = str(BASE_DIR / "data")
OUTPUT_DIR = str(BASE_DIR / "output_verified")

