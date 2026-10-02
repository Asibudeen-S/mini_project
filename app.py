import os
import secrets
from pathlib import Path

import click 
from sqlalchemy import inspect, text
from dotenv import load_dotenv
from flask import Flask, flash, redirect, url_for
from flask_login import current_user

from extensions import csrf, db, login_manager


load_dotenv()


def get_instance_secret(instance_path):
    """Return a stable secret key when SECRET_KEY is not configured."""
    configured = os.getenv("SECRET_KEY")
    if configured:
        return configured

    Path(instance_path).mkdir(parents=True, exist_ok=True)
    secret_path = Path(instance_path) / ".secret_key"
    try:
        secret = secret_path.read_text(encoding="utf-8").strip()
        if secret:
            return secret
    except FileNotFoundError:
        pass

    secret = secrets.token_hex(32)
    try:
        descriptor = os.open(secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        # Another worker may have created it between the read and exclusive create.
        return secret_path.read_text(encoding="utf-8").strip()
    with os.fdopen(descriptor, "w", encoding="utf-8") as secret_file:
        secret_file.write(secret)
    return secret


def upgrade_legacy_schema():
    """Add batch and timetable fields to databases created by earlier versions."""
    additions = {
        "user": {"study_year": "INTEGER"},
        "subject": {
            "study_year": "INTEGER NOT NULL DEFAULT 1",
            "weekday": "VARCHAR(9)",
            "start_time": "VARCHAR(5)",
            "end_time": "VARCHAR(5)",
            "room": "VARCHAR(80)",
        },
    }
    with db.engine.begin() as connection:
        inspector = inspect(connection)
        for table, columns in additions.items():
            present = {column["name"] for column in inspector.get_columns(table)}
            for name, definition in columns.items():
                if name not in present:
                    dialect = db.engine.dialect.identifier_preparer
                    quoted_table = dialect.quote(table)
                    quoted_name = dialect.quote(name)
                    connection.execute(text(
                        f"ALTER TABLE {quoted_table} ADD COLUMN {quoted_name} {definition}"))


def create_app(test_config=None):
    application = Flask(__name__, instance_relative_config=True)
    application.config.from_mapping(
        SECRET_KEY=get_instance_secret(application.instance_path),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///attendance.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
        UPLOAD_FOLDER=os.path.join(application.instance_path, "uploads"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "0") == "1",
    )
    if test_config:
        application.config.update(test_config)
    if application.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
        application.config["SQLALCHEMY_DATABASE_URI"] = application.config["SQLALCHEMY_DATABASE_URI"].replace("postgres://", "postgresql://", 1)
    Path(application.instance_path).mkdir(parents=True, exist_ok=True)
    Path(application.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(application)
    login_manager.init_app(application)
    csrf.init_app(application)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))

    @application.before_request
    def reject_inactive_accounts():
        if current_user.is_authenticated and current_user.status != "active":
            from flask_login import logout_user
            logout_user()
            flash("Your account is not active. Contact an administrator.", "warning")
            return redirect(url_for("main.login"))

    @application.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if current_user.is_authenticated:
            response.headers["Cache-Control"] = "private, no-store"
        return response

    with application.app_context():
        import models  # noqa: F401
        db.create_all()
        upgrade_legacy_schema()
        from routes import bp
        application.register_blueprint(bp)

    @application.errorhandler(413)
    def file_too_large(_error):
        flash("The uploaded file is larger than the 8 MB limit.", "danger")
        destination = url_for("main.dashboard") if current_user.is_authenticated else url_for("main.login")
        return redirect(destination)

    @application.cli.command("create-admin")
    def create_admin_command():
        """Create the first administrator account from an interactive prompt."""
        from sqlalchemy import func
        from models import User

        if User.query.filter_by(role="admin").first():
            raise click.ClickException("An administrator account already exists. This app allows one admin account.")
        name = click.prompt("Administrator name")
        email = click.prompt("Administrator email").strip().lower()
        if User.query.filter(func.lower(User.email) == email).first():
            raise click.ClickException("An account with that email already exists.")
        password = click.prompt("Password (at least 10 characters)", hide_input=True, confirmation_prompt=True)
        if len(password) < 10:
            raise click.ClickException("Password must contain at least 10 characters.")
        user = User(name=name.strip(), email=email, role="admin", status="active")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Administrator account created for {email}.")

    @application.cli.command("reset-admin-password")
    def reset_admin_password_command():
        """Set a new password for the existing single administrator account."""
        from models import User

        admins = User.query.filter_by(role="admin").all()
        if len(admins) != 1:
            raise click.ClickException(
                f"Expected exactly one administrator, found {len(admins)}."
            )
        password = click.prompt("New administrator password (at least 10 characters)",
                                hide_input=True, confirmation_prompt=True)
        if len(password) < 10:
            raise click.ClickException("Password must contain at least 10 characters.")
        admins[0].set_password(password)
        db.session.commit()
        click.echo(f"Administrator password updated for {admins[0].email}.")

    @application.context_processor
    def inject_globals():
        from datetime import date, datetime
        return {
            "current_year": date.today().year,
            "now": datetime.now,
        }

    return application


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
