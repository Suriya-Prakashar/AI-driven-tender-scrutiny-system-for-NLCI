from flask import Blueprint, jsonify

from app.services.pdf_service import clear_all_files

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "nlcil-tender-scrutiny-api"})


@health_bp.route("/api/home/clear", methods=["POST"])
def clear_on_home():
    """Clear temporary files when user returns to home (matches original behavior)."""
    clear_all_files()
    return jsonify({"success": True, "message": "Temporary files cleared."})
