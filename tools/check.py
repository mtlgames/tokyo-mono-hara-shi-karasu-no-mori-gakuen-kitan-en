"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it; exit code gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    tests = subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT)
    # text lint: every shipped English line within its width/byte budget, control codes and names matched
    lint = subprocess.call([sys.executable, "-X", "utf8", str(ROOT / "tools" / "batches.py"), "check"], cwd=ROOT)
    sys.exit(tests or lint)
