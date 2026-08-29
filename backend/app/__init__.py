from flask import Flask, jsonify
from flask_cors import CORS

from app.api.routes.evaluation_routes import evaluation_bp
from app.api.routes.health_routes import health_bp
from app.api.routes.merge_routes import merge_bp
from app.api.routes.upload_routes import upload_bp
from app.api.routes.udyam_routes import udyam_bp
from app.api.routes.workflow_routes import workflow_bp
from app.core.config import Config
from app.core.logging import setup_logging


def create_app() -> Flask:
    setup_logging()
    Config.ensure_directories()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH

    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

    app.register_blueprint(health_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(merge_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(workflow_bp)
    app.register_blueprint(udyam_bp)

    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify({"success": False, "message": "File too large."}), 413

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"success": False, "message": "Resource not found."}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"success": False, "message": "Internal server error."}), 500

    return app
