"""Run non-training checks before launching the lab experiment."""
from pathlib import Path
import subprocess
import sys

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    commands = [['_frozen.py'], ['replay_data.py'],
                ['-m', 'unittest', 'test_replay', 'test_bundle', '-v'], ['tests_marl.py']]
    for args in commands:
        subprocess.run([sys.executable, *args], cwd=root, check=True)
    print('All replay checks passed. No training was started.')
