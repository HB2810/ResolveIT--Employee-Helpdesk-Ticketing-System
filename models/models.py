from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


def utc_now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="employee")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

    tickets = db.relationship("Ticket", backref="employee", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(20), nullable=False, default="Open")
    admin_remark = db.Column(db.Text, nullable=True)
    attachment_filename = db.Column(db.String(255), nullable=True)
    attachment_original_name = db.Column(db.String(255), nullable=True)
    attachment_type = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    @property
    def age_hours(self):
        created_at = self.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return max(0, int((utc_now() - created_at).total_seconds() // 3600))

    @property
    def pulse_score(self):
        if self.status in ("Resolved", "Closed"):
            return 0

        priority_weight = {
            "Low": 14,
            "Medium": 28,
            "High": 46,
            "Critical": 64,
        }.get(self.priority, 28)
        status_weight = {
            "Open": 16,
            "In Progress": 8,
        }.get(self.status, 0)
        age_weight = min(28, self.age_hours // 4)
        return min(100, priority_weight + status_weight + age_weight)

    @property
    def pulse_label(self):
        score = self.pulse_score
        if score >= 80:
            return "Critical attention"
        if score >= 60:
            return "Needs attention"
        if score >= 35:
            return "Monitoring"
        if score > 0:
            return "Stable"
        return "Completed"

    @property
    def pulse_class(self):
        score = self.pulse_score
        if score >= 80:
            return "pulse-critical"
        if score >= 60:
            return "pulse-warning"
        if score >= 35:
            return "pulse-watch"
        if score > 0:
            return "pulse-stable"
        return "pulse-done"

    @property
    def next_best_action(self):
        if self.status == "Open":
            return "Review and begin triage"
        if self.status == "In Progress":
            return "Post an update or resolve"
        if self.status == "Resolved":
            return "Confirm resolution"
        return "No action needed"

    @property
    def has_attachment(self):
        return bool(self.attachment_filename)

    @property
    def attachment_is_image(self):
        return self.attachment_type == "image"

    @property
    def attachment_is_video(self):
        return self.attachment_type == "video"
