"""DARPA OpTC audit entry point. Requires the shared ../audit_core.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import audit_core
import config

def run_download():
    """Read local labelled records; never fabricate or download fallback data."""
    return audit_core.ingest(config.DATA_DIR, config.OUTPUT_DIR)

if __name__ == "__main__":
    run_download()

