"""Validate local Mordor metadata. No downloads or built-in examples."""
from pathlib import Path
import config

def run_download():
    root = Path(config.DATA_DIR)
    if not root.is_dir():
        raise FileNotFoundError(f"Metadata directory missing: {root}. Use --repo PATH.")
    return sorted(set(root.rglob("*.yaml")) | set(root.rglob("*.yml")))

if __name__ == "__main__":
    run_download()

