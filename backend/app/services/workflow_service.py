import logging
import uuid
from datetime import datetime, timezone

import requests

from app.core.config import Config

logger = logging.getLogger(__name__)

# In-memory job store (replace with Redis/DB for production multi-worker setups)
_jobs: dict[str, dict] = {}


def _create_job(job_type: str, files: list[str]) -> str:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "type": job_type,
        "status": "running",
        "files": files,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "message": f"{job_type} started",
        "error": None,
    }
    return job_id


def _complete_job(job_id: str, success: bool, message: str, error: str | None = None) -> None:
    if job_id not in _jobs:
        return
    _jobs[job_id].update(
        {
            "status": "completed" if success else "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "message": message,
            "error": error,
        }
    )


def get_job_status(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def trigger_evaluation(files: list[str]) -> dict:
    """Trigger n8n evaluation workflow and return job result."""
    job_id = _create_job("evaluation", files)
    webhook_url = Config.evaluation_webhook_url()

    try:
        response = requests.post(
            webhook_url,
            json={"files": files},
            headers={"Content-Type": "application/json"},
            timeout=600,
        )
        if response.ok:
            _complete_job(job_id, True, "Evaluation completed successfully")
            return {
                "job_id": job_id,
                "status": "completed",
                "message": "Evaluation completed successfully",
                "google_sheets_url": Config.GOOGLE_SHEETS_URL,
            }

        error_msg = f"Evaluation workflow returned status {response.status_code}"
        _complete_job(job_id, False, "Evaluation failed", error_msg)
        return {"job_id": job_id, "status": "failed", "message": error_msg}

    except requests.RequestException as exc:
        logger.exception("Evaluation webhook failed: %s", exc)
        _complete_job(job_id, False, "Unable to reach evaluation server", str(exc))
        return {
            "job_id": job_id,
            "status": "failed",
            "message": "Unable to reach evaluation server",
            "error": str(exc),
        }


def trigger_udyam_webhook(files: list[str]) -> dict:
    """Trigger n8n Udyam workflow webhook."""
    job_id = _create_job("udyam_webhook", files)
    webhook_url = Config.udyam_webhook_url()

    if "YOUR_UDYAM_WEBHOOK_ID" in webhook_url:
        _complete_job(
            job_id,
            False,
            "Udyam webhook not configured",
            "Set N8N_UDYAM_WEBHOOK in .env",
        )
        return {
            "job_id": job_id,
            "status": "failed",
            "message": "Udyam webhook not configured. Set N8N_UDYAM_WEBHOOK in .env",
        }

    try:
        response = requests.post(
            webhook_url,
            json={"files": files},
            headers={"Content-Type": "application/json"},
            timeout=600,
        )
        if response.ok:
            _complete_job(job_id, True, "Udyam verification completed")
            return {
                "job_id": job_id,
                "status": "completed",
                "message": "Udyam verification completed",
            }

        error_msg = f"Udyam workflow returned status {response.status_code}"
        _complete_job(job_id, False, "Udyam process failed", error_msg)
        return {"job_id": job_id, "status": "failed", "message": error_msg}

    except requests.RequestException as exc:
        logger.exception("Udyam webhook failed: %s", exc)
        _complete_job(job_id, False, "Unable to reach Udyam server", str(exc))
        return {
            "job_id": job_id,
            "status": "failed",
            "message": "Unable to reach Udyam server",
            "error": str(exc),
        }
