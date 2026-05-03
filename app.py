from pathlib import Path

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import inspect

from config import Config
from config import IS_VERCEL
from models.models import db, User
from routes.routes import main_bp


mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"

talisman = Talisman()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    static_folder = "public/static" if IS_VERCEL else "static"
    app = Flask(__name__, static_folder=static_folder, static_url_path="/static")
    app.config.from_object(Config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    if not IS_VERCEL:
        Path("database").mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Initialize security headers (only enforce in production)
    if not app.debug:
        csp = {
            'default-src': ["'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://fonts.gstatic.com"],
            'script-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
            'style-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com"],
            'img-src': ["'self'", "data:"],
            'font-src': ["'self'", "https://cdnjs.cloudflare.com", "https://fonts.gstatic.com"]
        }
        talisman.init_app(app, content_security_policy=csp, force_https=False)
    
    limiter.init_app(app)
    
    app.register_blueprint(main_bp)

    # Custom Jinja filter: convert UTC datetime to IST
    from datetime import timedelta, timezone as tz
    IST = tz(timedelta(hours=5, minutes=30))
    
    @app.template_filter('to_ist')
    def to_ist_filter(dt):
        if dt is None:
            return ''
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz.utc)
        return dt.astimezone(IST).strftime("%b %d, %Y, %I:%M %p")

    with app.app_context():
        db.create_all()
        ensure_ticket_attachment_columns()
        create_sample_admin()

    return app


def create_sample_admin():
    admin_email = "admin@example.com"
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            username="Helpdesk Admin",
            email=admin_email,
            role="admin",
        )
        admin.set_password("Admin@123")
        db.session.add(admin)
        db.session.commit()


def ensure_ticket_attachment_columns():
    inspector = inspect(db.engine)
    if "tickets" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("tickets")}
    attachment_columns = {
        "attachment_filename": "VARCHAR(255)",
        "attachment_original_name": "VARCHAR(255)",
        "attachment_type": "VARCHAR(20)",
    }

    with db.engine.begin() as connection:
        for column_name, column_type in attachment_columns.items():
            if column_name not in existing_columns:
                connection.exec_driver_sql(f"ALTER TABLE tickets ADD COLUMN {column_name} {column_type}")


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
