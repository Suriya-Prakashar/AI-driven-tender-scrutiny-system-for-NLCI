from flask import Blueprint, jsonify, request

from app.services.pdf_service import list_files
from app.services.workflow_service import get_job_status, trigger_evaluation

workflow_bp = Blueprint("workflow", __name__, url_prefix="/api/workflow")


@workflow_bp.route("/start", methods=["POST"])
def start_workflow():
    payload = request.get_json(silent=True) or {}
    files = payload.get("files") or list_files()

    if not files:
        return jsonify({"success": False, "message": "No PDF files available."}), 400

    result = trigger_evaluation(files)
    status_code = 200 if result.get("status") == "completed" else 502
    return jsonify({"success": result.get("status") == "completed", **result}), status_code


@workflow_bp.route("/status/<job_id>", methods=["GET"])
def workflow_status(job_id):
    job = get_job_status(job_id)
    if not job:
        return jsonify({"success": False, "message": "Job not found."}), 404
    return jsonify(job)
