import threading

from flask import Blueprint, jsonify, request

from app.services.pdf_service import list_files
from app.services.udyam_service import run_udyam_verification
from app.services.workflow_service import get_job_status, trigger_udyam_webhook

udyam_bp = Blueprint("udyam", __name__, url_prefix="/api/udyam")

_udyam_jobs: dict[str, dict] = {}


@udyam_bp.route("/verify", methods=["POST"])
def verify_udyam():
    payload = request.get_json(silent=True) or {}
    mode = payload.get("mode", "webhook")
    files = payload.get("files") or list_files()

    if mode == "selenium":
        job_id = f"udyam-{len(_udyam_jobs) + 1}"

        def _run():
            try:
                result = run_udyam_verification(payload.get("excel_path"))
                _udyam_jobs[job_id] = {"status": "completed", **result}
            except Exception as exc:
                _udyam_jobs[job_id] = {"status": "failed", "message": str(exc)}

        _udyam_jobs[job_id] = {"status": "running", "message": "Udyam verification in progress"}
        threading.Thread(target=_run, daemon=True).start()
        return jsonify({"success": True, "job_id": job_id, "status": "running"})

    result = trigger_udyam_webhook(files)
    status_code = 200 if result.get("status") == "completed" else 502
    return jsonify({"success": result.get("status") == "completed", **result}), status_code


@udyam_bp.route("/status/<job_id>", methods=["GET"])
def udyam_status(job_id):
    if job_id in _udyam_jobs:
        return jsonify(_udyam_jobs[job_id])

    job = get_job_status(job_id)
    if not job:
        return jsonify({"success": False, "message": "Job not found."}), 404
    return jsonify(job)
