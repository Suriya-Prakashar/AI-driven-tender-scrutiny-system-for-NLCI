from flask import Blueprint, jsonify, request, send_file

from app.services.pdf_service import (
    clear_all_files,
    delete_file,
    get_download_path,
    list_files,
    save_uploaded_files,
)

upload_bp = Blueprint("upload", __name__, url_prefix="/api/files")


@upload_bp.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")
    saved, error = save_uploaded_files(files)
    if error:
        return jsonify({"success": False, "message": error}), 400
    return jsonify({"success": True, "message": "File(s) uploaded successfully", "files": saved})


@upload_bp.route("", methods=["GET"])
def get_files():
    return jsonify({"files": list_files()})


@upload_bp.route("/clear", methods=["POST"])
def clear_files():
    clear_all_files()
    return jsonify({"success": True, "message": "Cleared all temporary files."})


@upload_bp.route("/<path:filename>", methods=["DELETE"])
def remove_file(filename):
    success, message = delete_file(filename)
    status = 200 if success else 404
    return jsonify({"success": success, "message": message}), status


@upload_bp.route("/<path:filename>/download", methods=["GET"])
def download(filename):
    path = get_download_path(filename)
    if not path:
        return jsonify({"success": False, "message": f"File '{filename}' not found."}), 404
    return send_file(path, as_attachment=True, download_name=path.name)
