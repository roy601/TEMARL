"""Verify the file hashes in the distributed S1 archive (no dependencies)."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parents[1]
count = 0
for line in (root/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
    digest, name = line.split('  ', 1)
    path = (root/name).resolve()
    assert path.is_relative_to(root), 'Invalid manifest path'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
    count += 1
print(f'All {count} distributed file hashes verified.')
