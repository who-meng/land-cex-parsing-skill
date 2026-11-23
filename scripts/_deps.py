"""Use dependencies installed from the wheels shipped in this package."""
from pathlib import Path
import sys
folder = Path(__file__).resolve().parents[1] / "deps" / "1"
if folder.is_dir():
    sys.path.insert(0, str(folder))
