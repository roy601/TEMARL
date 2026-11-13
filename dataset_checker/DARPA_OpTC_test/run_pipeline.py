"""DARPA OpTC audit entry point. Requires the shared ../audit_core.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import audit_core
import config

if __name__ == "__main__":
    audit_core.main(Path(__file__).resolve().parent, "DARPA OpTC")

