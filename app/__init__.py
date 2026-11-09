"""Flask application factory for Exalted Chronicle."""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask

from config import Config
from .extensions import csrf, db, login_manager


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    log_directory = os.path.join(app.instance_path, "logs")
    os.makedirs(log_directory, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Sign in to enter this part of Creation."
    login_manager.login_message_category = "info"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    from .routes import main
    app.register_blueprint(main)

    if not app.testing:
        handler = RotatingFileHandler(
            os.path.join(log_directory, "exalted.log"), maxBytes=1_000_000, backupCount=3
        )
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        handler.setLevel(logging.DEBUG)
        if not any(isinstance(existing, RotatingFileHandler) for existing in app.logger.handlers):
            app.logger.addHandler(handler)
        app.logger.setLevel(logging.DEBUG)

    with app.app_context():
        db.create_all()
        app.logger.info("Exalted Chronicle application initialized")

    return app
