from flask import Blueprint, jsonify, request

from app.services.merge_service import get_merge_file_list, merge_pdfs

merge_bp = Blueprint("merge", __name__, url_prefix="/api/merge")


@merge_bp.route("", methods=["POST"])
def merge():
    files = request.files.getlist("files")
    merged_filename = request.form.get("merged_filename", "")
    result_name, error = merge_pdfs(files, merged_filename)
    if error:
        return jsonify({"success": False, "message": error}), 400
    return jsonify(
        {
            "success": True,
            "message": "PDF files merged successfully!",
            "merged_file": result_name,
            "files": get_merge_file_list(),
        }
    )


@merge_bp.route("/files", methods=["GET"])
def merge_files():
    return jsonify({"files": get_merge_file_list()})
