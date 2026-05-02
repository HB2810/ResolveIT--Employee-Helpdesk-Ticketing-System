from functools import wraps
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from forms.forms import LoginForm, RegistrationForm, TicketForm, TicketUpdateForm
from models.models import Ticket, User, db


main_bp = Blueprint("main", __name__)

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
VIDEO_EXTENSIONS = {"mp4", "mov", "webm"}


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("main.login", next=request.url))
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped_view


def save_ticket_attachment(file_storage):
    if not file_storage or not file_storage.filename:
        return None, None, None

    original_name = secure_filename(file_storage.filename)
    extension = Path(original_name).suffix.lower().lstrip(".")
    media_type = "image" if extension in IMAGE_EXTENSIONS else "video"
    stored_name = f"{uuid4().hex}.{extension}"
    upload_path = Path(current_app.config["UPLOAD_FOLDER"])
    upload_path.mkdir(parents=True, exist_ok=True)
    file_storage.save(upload_path / stored_name)
    return stored_name, original_name, media_type


@main_bp.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@main_bp.app_errorhandler(403)
def forbidden(error):
    return render_template("error.html", code=403, message="You do not have permission to access this page."), 403


@main_bp.app_errorhandler(404)
def page_not_found(error):
    return render_template("error.html", code=404, message="The page you requested could not be found."), 404


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("main.admin_dashboard"))
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "danger")
            return render_template("register.html", form=form)

        user = User(username=form.username.data.strip(), email=email, role="employee")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please sign in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Welcome back.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("main.admin_dashboard"))

    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    active_tickets = [ticket for ticket in tickets if ticket.status not in ("Resolved", "Closed")]
    attention_ticket = max(active_tickets, key=lambda ticket: ticket.pulse_score, default=None)
    stats = {
        "total": len(tickets),
        "open": sum(1 for ticket in tickets if ticket.status == "Open"),
        "progress": sum(1 for ticket in tickets if ticket.status == "In Progress"),
        "resolved": sum(1 for ticket in tickets if ticket.status == "Resolved"),
        "closed": sum(1 for ticket in tickets if ticket.status == "Closed"),
        "attention": sum(1 for ticket in active_tickets if ticket.pulse_score >= 60),
    }
    return render_template("dashboard.html", tickets=tickets, stats=stats, attention_ticket=attention_ticket)


@main_bp.route("/tickets/create", methods=["GET", "POST"])
@login_required
def create_ticket():
    if current_user.is_admin:
        flash("Admin users manage tickets from the admin dashboard.", "info")
        return redirect(url_for("main.admin_dashboard"))

    form = TicketForm()
    if form.validate_on_submit():
        filename, original_name, media_type = save_ticket_attachment(form.attachment.data)
        ticket = Ticket(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            priority=form.priority.data,
            attachment_filename=filename,
            attachment_original_name=original_name,
            attachment_type=media_type,
            user_id=current_user.id,
        )
        db.session.add(ticket)
        db.session.commit()
        flash("Your support ticket has been created.", "success")
        return redirect(url_for("main.ticket_details", ticket_id=ticket.id))

    return render_template("create_ticket.html", form=form)


@main_bp.route("/tickets/<int:ticket_id>")
@login_required
def ticket_details(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not current_user.is_admin and ticket.user_id != current_user.id:
        abort(403)

    form = TicketUpdateForm(obj=ticket)
    return render_template("ticket_details.html", ticket=ticket, form=form)


@main_bp.route("/admin/dashboard")
@login_required
@admin_required
def admin_dashboard():
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    active_tickets = [ticket for ticket in tickets if ticket.status not in ("Resolved", "Closed")]
    priority_queue = sorted(active_tickets, key=lambda ticket: ticket.pulse_score, reverse=True)[:5]
    stats = {
        "total": len(tickets),
        "open": sum(1 for ticket in tickets if ticket.status == "Open"),
        "progress": sum(1 for ticket in tickets if ticket.status == "In Progress"),
        "resolved": sum(1 for ticket in tickets if ticket.status == "Resolved"),
        "closed": sum(1 for ticket in tickets if ticket.status == "Closed"),
        "attention": sum(1 for ticket in active_tickets if ticket.pulse_score >= 60),
    }
    return render_template(
        "admin_dashboard.html",
        tickets=tickets[:8],
        stats=stats,
        priority_queue=priority_queue,
    )


@main_bp.route("/admin/tickets")
@login_required
@admin_required
def manage_tickets():
    status_filter = request.args.get("status", "All")
    priority_filter = request.args.get("priority", "All")
    search_query = request.args.get("q", "").strip()
    query = Ticket.query
    if status_filter != "All":
        query = query.filter_by(status=status_filter)
    if priority_filter != "All":
        query = query.filter_by(priority=priority_filter)
    if search_query:
        like_query = f"%{search_query}%"
        query = query.join(User).filter(
            or_(
                Ticket.title.ilike(like_query),
                Ticket.description.ilike(like_query),
                User.username.ilike(like_query),
                User.email.ilike(like_query),
            )
        )
    tickets = query.order_by(Ticket.created_at.desc()).all()
    tickets = sorted(tickets, key=lambda ticket: ticket.pulse_score, reverse=True)
    return render_template(
        "manage_tickets.html",
        tickets=tickets,
        status_filter=status_filter,
        priority_filter=priority_filter,
        search_query=search_query,
    )


@main_bp.route("/admin/tickets/<int:ticket_id>/update", methods=["POST"])
@login_required
@admin_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form = TicketUpdateForm()
    if form.validate_on_submit():
        ticket.status = form.status.data
        ticket.priority = form.priority.data
        ticket.admin_remark = form.admin_remark.data.strip() if form.admin_remark.data else None
        db.session.commit()
        flash("Ticket updated successfully.", "success")
    else:
        flash("Please review the ticket update form.", "danger")
    return redirect(url_for("main.ticket_details", ticket_id=ticket.id))
