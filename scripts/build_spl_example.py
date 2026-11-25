"""Build the standalone SPL example from the package implementation."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


root = Path(__file__).resolve().parents[1]
project = root / "python" / "pyacdete"
example = project / "examples" / "spl_leq"
files = (
    project / "pyacdete" / "spl_leq.py",
    example / "sti_spl_example.py",
    example / "requirements.txt",
    example / "README.md",
)

with ZipFile(root / "docs" / "downloads" / "spl_leq_example.zip", "w") as archive:
    for source in files:
        # ZipInfo's fixed timestamp keeps the download identical across rebuilds.
        entry = ZipInfo(source.name)
        entry.create_system = 3
        entry.external_attr = 0o644 << 16
        archive.writestr(entry, source.read_bytes(), compress_type=ZIP_DEFLATED)
