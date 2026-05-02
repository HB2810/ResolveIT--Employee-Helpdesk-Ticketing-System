from pathlib import Path

from flask import Flask
from flask_login import LoginManager
from sqlalchemy import inspect

from config import Config
from models.models import db, User
from routes.routes import main_bp


login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path("database").mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(main_bp)

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
