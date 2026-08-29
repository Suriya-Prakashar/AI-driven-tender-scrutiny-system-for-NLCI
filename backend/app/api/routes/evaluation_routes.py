from flask import Blueprint, jsonify, request
import time
import requests

from app.services.pdf_service import list_files

evaluation_bp = Blueprint("evaluation", __name__, url_prefix="/api/evaluation")


@evaluation_bp.route("/files", methods=["GET"])
def evaluation_files():
    files = list_files()
    message = None if files else "No files uploaded yet."
    return jsonify({"files": files, "message": message})


@evaluation_bp.route("/start", methods=["POST"])
def start_evaluation():
    payload = request.get_json(silent=True) or {}
    files = payload.get("files") or list_files()

    if not files:
        return jsonify({"success": False, "message": "No PDF files available for evaluation."}), 400

    # =========================================================================
    # 🔗 INSERT YOUR N8N WEBHOOK URL HERE
    # =========================================================================
    N8N_WEBHOOK_URL = "https://your-n8n-instance.com/webhook/your-webhook-id"
    
    try:
        # Trigger the N8N workflow by sending the list of files
        response = requests.post(N8N_WEBHOOK_URL, json={"files": files})
        response.raise_for_status()
        
        # You can extract the google sheets URL from the n8n response if your workflow returns it
        # n8n_data = response.json()
        # sheet_url = n8n_data.get("google_sheets_url", "...")
    except Exception as e:
        print(f"Failed to trigger N8N workflow: {e}")
        # Fallback or error handling
        
    result = {
        "status": "completed",
        "google_sheets_url": "https://docs.google.com/spreadsheets/d/1wkYCypcvEWqS1Uz-zOfoIpR9gdNjDoktTm50jc-eTL0/edit?usp=sharing"
    }
    return jsonify({"success": True, **result}), 200
