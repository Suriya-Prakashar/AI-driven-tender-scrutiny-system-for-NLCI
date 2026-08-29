import logging
import os
from pathlib import Path

from werkzeug.utils import secure_filename

from app.core.config import Config
from app.utils.file_utils import allowed_file, safe_path, unique_path

logger = logging.getLogger(__name__)


def clear_folder(folder_path: Path) -> None:
    """Delete all files and directories inside a given folder."""
    if not folder_path.is_dir():
        return
    for item in folder_path.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                import shutil
                shutil.rmtree(item)
        except OSError as exc:
            logger.error("Failed to delete %s: %s", item, exc)


def list_files() -> list[str]:
    """List PDF files in the upload directory."""
    Config.ensure_directories()
    return sorted(
        f.name
        for f in Config.UPLOAD_DIR.iterdir()
        if f.is_file() and f.suffix.lower() == ".pdf"
    )


def save_uploaded_files(file_storage_list) -> tuple[list[str], str | None]:
    """
    Save uploaded PDF files directly to UPLOAD_DIR.
    Returns (saved_filenames, error_message).
    """
    Config.ensure_directories()
    saved = []

    if not file_storage_list or all(not f.filename for f in file_storage_list):
        return [], "Please select at least one PDF file."

    for file_storage in file_storage_list:
        if not file_storage.filename:
            continue
        if not allowed_file(file_storage.filename):
            return saved, f"Invalid file type: {file_storage.filename}. Only PDF files are allowed."

        safe_name = secure_filename(file_storage.filename)
        dest = unique_path(Config.UPLOAD_DIR / safe_name)
        file_storage.save(dest)
        saved.append(dest.name)

    if not saved:
        return [], "Please select at least one PDF file."

    return saved, None


def delete_file(filename: str) -> tuple[bool, str]:
    try:
        deleted = False
        file_path = safe_path(Config.UPLOAD_DIR, filename)
        if file_path and file_path.exists():
            file_path.unlink()
            deleted = True

        merged_path = safe_path(Config.MERGED_DIR, filename)
        if merged_path and merged_path.exists():
            merged_path.unlink()
            deleted = True

        if deleted:
            return True, f"File '{filename}' deleted successfully."
        else:
            return False, f"File '{filename}' not found."
    except Exception as exc:
        logger.exception("Failed to delete file %s: %s", filename, exc)
        return False, f"Failed to delete file: {exc}"


def get_download_path(filename: str) -> Path | None:
    file_path = safe_path(Config.UPLOAD_DIR, filename)
    if file_path and file_path.exists():
        return file_path
    return None


def clear_all_files() -> None:
    clear_folder(Config.UPLOAD_DIR)
    clear_folder(Config.MERGED_DIR)
