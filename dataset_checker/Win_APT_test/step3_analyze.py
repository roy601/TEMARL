"""Windows APT audit entry point. Requires the shared ../audit_core.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import audit_core
import config

def analyze_sequences():
    return audit_core.analyze(config.OUTPUT_DIR, "Windows APT")

if __name__ == "__main__":
    analyze_sequences()

