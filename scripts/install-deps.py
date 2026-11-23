"""Install the bundled Python dependencies without accessing a package index."""
from pathlib import Path
import hashlib
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
wheels = root / "wheels"
for line in (wheels / "SHA256SUMS").read_text(encoding="ascii").splitlines():
    expected, name = line.split()
    if Path(name).name != name or hashlib.sha256((wheels / name).read_bytes()).hexdigest() != expected:
        raise RuntimeError("Bundled dependency checksum mismatch: " + name)
result = subprocess.run([sys.executable, "-m", "pip", "--isolated", "--disable-pip-version-check", "install",
    "--no-index", "--find-links", str(wheels), "--only-binary=:all:", "--no-compile",
    "--target", str(root / "deps" / "1"), "comtypes==1.4.15", "openpyxl==3.1.5", "et_xmlfile==2.0.0"])
sys.exit(result.returncode)
