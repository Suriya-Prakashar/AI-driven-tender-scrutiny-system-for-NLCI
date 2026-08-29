import os
from pathlib import Path

from werkzeug.utils import secure_filename

from app.core.config import Config


def allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


def safe_path(folder: Path, filename: str) -> Path | None:
    """Resolve a safe file path inside folder, preventing path traversal."""
    safe_name = secure_filename(filename)
    if not safe_name:
        return None

    folder_abs = folder.resolve()
    file_path = (folder_abs / safe_name).resolve()

    if not str(file_path).startswith(str(folder_abs) + os.sep) and file_path != folder_abs:
        return None

    return file_path


def unique_path(base_path: Path) -> Path:
    """Return a non-colliding path by appending _1, _2, ... before extension."""
    if not base_path.exists():
        return base_path

    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent
    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
