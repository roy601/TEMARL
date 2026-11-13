"""DARPA OpTC audit entry point. Requires the shared ../audit_core.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import audit_core
import config

def extract_sequences():
    return audit_core.extract(config.OUTPUT_DIR)

if __name__ == "__main__":
    extract_sequences()

