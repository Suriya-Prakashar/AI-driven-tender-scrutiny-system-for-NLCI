import logging
from pathlib import Path

from PyPDF2 import PdfMerger
from werkzeug.utils import secure_filename

from app.core.config import Config
from app.services.pdf_service import clear_folder, list_files
from app.utils.file_utils import allowed_file, unique_path

logger = logging.getLogger(__name__)


def merge_pdfs(file_storage_list, merged_filename: str) -> tuple[str | None, str | None]:
    """
    Merge uploaded PDFs into a single file in UPLOAD_DIR.
    Returns (merged_filename, error_message).
    """
    Config.ensure_directories()

    if not file_storage_list or all(not f.filename for f in file_storage_list):
        return None, "Please select at least one PDF file to merge."

    if not merged_filename or not merged_filename.strip():
        return None, "Please provide a name for the merged file."

    merged_name = merged_filename.strip()
    if not merged_name.lower().endswith(".pdf"):
        merged_name += ".pdf"
    merged_name = secure_filename(merged_name)

    clear_folder(Config.MERGED_DIR)

    merger = PdfMerger()
    temp_files: list[Path] = []
    partial_files: list[Path] = []

    try:
        # Save all files with unique indexed names to prevent name collisions
        for i, file_storage in enumerate(file_storage_list):
            if not file_storage.filename:
                continue
            if not allowed_file(file_storage.filename):
                return None, f"Invalid file type: {file_storage.filename}. Only PDF files are allowed."

            temp_path = Config.MERGED_DIR / f"temp_{i}_{secure_filename(file_storage.filename)}"
            file_storage.save(temp_path)
            temp_files.append(temp_path)

        if not temp_files:
            return None, "Please select at least one PDF file to merge."

        merged_path = unique_path(Config.UPLOAD_DIR / merged_name)

        if len(temp_files) == 1:
            # If only one file is provided, copy it directly to destination
            import shutil
            shutil.copy(str(temp_files[0]), str(merged_path))
        else:
            # Incremental one-by-one merge to keep file handles limit minimal
            current_merged = temp_files[0]
            for idx, next_file in enumerate(temp_files[1:]):
                partial_path = Config.MERGED_DIR / f"partial_{idx}.pdf"
                
                with PdfMerger() as merger:
                    merger.append(str(current_merged), import_outline=False)
                    merger.append(str(next_file), import_outline=False)
                    merger.write(str(partial_path))

                # Clean up previous partial file if it was created in this loop
                if current_merged != temp_files[0]:
                    try:
                        current_merged.unlink()
                    except OSError as exc:
                        logger.error("Failed to delete intermediate partial file %s: %s", current_merged, exc)

                current_merged = partial_path
                partial_files.append(partial_path)

            # Move final merged result to target destination
            import shutil
            shutil.move(str(current_merged), str(merged_path))

        return merged_path.name, None

    except Exception as exc:
        logger.exception("PDF merge failed: %s", exc)
        return None, f"Failed to merge PDFs: {exc}"

    finally:
        # Clean up all temporary files
        for path in temp_files + partial_files:
            try:
                if path.exists():
                    path.unlink()
            except OSError as exc:
                logger.error("Failed to delete temp file %s: %s", path, exc)


def get_merge_file_list() -> list[str]:
    return list_files()
