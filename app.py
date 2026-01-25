import os
import logging
from flask import (
    Flask, render_template, request, redirect, url_for,
    send_file, flash
)
from PyPDF2 import PdfMerger
from werkzeug.utils import secure_filename

# ------------------------ APP SETUP ------------------------

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Folder setup
UPLOAD_FOLDER = "uploads"   # final/working PDFs (used for evaluation, download)
MERGED_FOLDER = "merged"    # TEMP folder for merging only
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MERGED_FOLDER"] = MERGED_FOLDER

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------ HELPER FUNCTIONS ------------------------

def clear_folder(folder_path: str):
    """Delete all files inside a given folder."""
    if not os.path.isdir(folder_path):
        return
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.error(f'Failed to delete {file_path}: {e}')

def clear_uploads():
    """Delete all files inside the uploads folder (evaluation working set)."""
    clear_folder(app.config['UPLOAD_FOLDER'])

def clear_temp_merges():
    """Delete all files inside the merged (temporary) folder."""
    clear_folder(app.config['MERGED_FOLDER'])

# ------------------------ ROUTES ------------------------

@app.route("/")
def home():
    # When returning home, clean everything = temporary storage
    clear_uploads()
    clear_temp_merges()
    return render_template("page1.html")

@app.route("/merge_option", methods=["POST"])
def merge_option():
    # Button choice: "merge" or "continue"
    if request.form["action"] == "merge":
        return redirect(url_for("merge_page"))
    return redirect(url_for("workflow_status"))

@app.route("/merge", methods=["GET", "POST"])
def merge_page():
    if request.method == "POST":
        files = request.files.getlist("files")
        merged_name = request.form.get("merged_filename")

        # Basic validations
        if not files or all(file.filename == '' for file in files):
            return render_template(
                "page2.html",
                message="Please select at least one PDF file to merge.",
                files=os.listdir(app.config['UPLOAD_FOLDER'])
            )

        if not merged_name:
            return render_template(
                "page2.html",
                message="Please provide a name for the merged file.",
                files=os.listdir(app.config['UPLOAD_FOLDER'])
            )

        if not merged_name.lower().endswith(".pdf"):
            merged_name += ".pdf"

        # Ensure temp folder clean for this merge operation
        clear_temp_merges()

        merger = PdfMerger()
        temp_files = []

        # Save PDFs to TEMP folder and merge from there
        for file in files:
            if file.filename:
                temp_path = os.path.join(
                    app.config["MERGED_FOLDER"],
                    secure_filename(file.filename)
                )
                file.save(temp_path)
                merger.append(temp_path)
                temp_files.append(temp_path)

        # Final merged file goes into UPLOAD_FOLDER (used later for evaluation)
        merged_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            secure_filename(merged_name)
        )

        # Avoid overwriting an existing file with the same name
        if os.path.exists(merged_path):
            base, ext = os.path.splitext(merged_path)
            i = 1
            while os.path.exists(f"{base}_{i}{ext}"):
                i += 1
            merged_path = f"{base}_{i}{ext}"

        merger.write(merged_path)
        merger.close()

        # Cleanup temporary source files used for merging
        for file_path in temp_files:
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to delete temp file {file_path}: {e}")

        flash("PDF files merged successfully!", "success")
        # Redirect back to merge_page so user sees merged file in the list
        return redirect(url_for("merge_page"))

    # For GET, show current files in UPLOAD_FOLDER (temporary working set)
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("page2.html", files=files)

@app.route("/clear_merged_files", methods=["POST"])
def clear_merged_files():
    """
    Clear all working files:
      - Remove all PDFs in UPLOAD_FOLDER (merged or uploaded)
      - Remove any temp merge files in MERGED_FOLDER
    """
    try:
        clear_uploads()
        clear_temp_merges()
        flash("Cleared all temporary files.", "info")
    except Exception as e:
        flash(f"Error clearing files: {e}", "error")

    return redirect(url_for("merge_page"))

@app.route("/delete_file/<path:filename>", methods=["POST", "GET"])
def delete_file(filename):
    """Delete a specific uploaded/merged file from UPLOAD_FOLDER."""
    try:
        safe_name = secure_filename(filename)
        folder = os.path.abspath(app.config["UPLOAD_FOLDER"])
        file_path = os.path.abspath(os.path.join(folder, safe_name))

        # Safety check: prevent path traversal
        if not file_path.startswith(folder + os.sep):
            flash("Invalid file path.", "error")
            return redirect(url_for("merge_page"))

        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f"File '{safe_name}' deleted successfully.", "success")
        else:
            flash(f"File '{safe_name}' not found.", "error")

    except Exception as e:
        flash(f"Error deleting file: {str(e)}", "error")

    return redirect(url_for("merge_page"))

@app.route("/upload", methods=["GET", "POST"])
def upload():
    """
    Separate upload route (if you use it on page3.html).
    Files stored in UPLOAD_FOLDER = temporary working set
    and cleared when going back home or via clear_merged_files.
    """
    if request.method == "POST":
        files = request.files.getlist("files")
        if not files or all(f.filename == '' for f in files):
            flash("Please upload at least one file.", "error")
            return render_template("page3.html")

        for file in files:
            if file.filename:
                path = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    secure_filename(file.filename)
                )
                file.save(path)

        flash("File(s) uploaded successfully!", "success")
        return redirect(url_for("evaluation"))

    return render_template("page3.html")

@app.route("/evaluation", methods=["GET", "POST"])
def evaluation():
    """Displays uploaded/merged files and lets user start evaluation."""
    files = [
        f for f in os.listdir(app.config['UPLOAD_FOLDER'])
        if f.lower().endswith('.pdf')
    ]

    if request.method == "POST":
        evaluation_type = request.form.get("evaluation_type")
        comments = request.form.get("comments", "")

        if not evaluation_type:
            flash("Please select an evaluation type.", "error")
            return render_template("page3.html", files=files)

        flash(f"Starting {evaluation_type} evaluation...", "success")
        return redirect(url_for(
            "workflow_status",
            evaluation_type=evaluation_type,
            file_count=len(files)
        ))

    message = "No files uploaded yet." if not files else None
    return render_template("page3.html", files=files, message=message)

@app.route("/workflow_status")
def workflow_status():
    """
    Display workflow status.
    NOTE: We keep files until user goes Home or uses Clear All Files.
    That makes storage temporary but still usable until they are done.
    """
    evaluation_type = request.args.get('evaluation_type', 'Unknown')
    file_count = request.args.get('file_count', 0)
    return render_template(
        "workflow_status.html",
        status="success",
        time_taken="0.00",
        evaluation_type=evaluation_type,
        file_count=file_count
    )

@app.route("/download/<filename>")
def download_file(filename):
    """Download a specific file from UPLOAD_FOLDER."""
    try:
        safe_name = secure_filename(filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
        else:
            flash(f"File '{safe_name}' not found.", "error")
            return redirect(url_for("evaluation"))
    except Exception as e:
        flash(f"Error downloading file: {e}", "error")
        return redirect(url_for("evaluation"))
    

if __name__ == "__main__":
    app.run(debug=True)
