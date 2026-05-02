from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import EmailField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class RegistrationForm(FlaskForm):
    username = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=80)])
    email = EmailField("Email Address", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = EmailField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class TicketForm(FlaskForm):
    title = StringField("Ticket Title", validators=[DataRequired(), Length(min=5, max=150)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=10)])
    priority = SelectField(
        "Priority",
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High"), ("Critical", "Critical")],
        default="Medium",
        validators=[DataRequired()],
    )
    attachment = FileField(
        "Error Screenshot or Video",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "gif", "webp", "mp4", "mov", "webm"],
                "Upload an image or video file only.",
            )
        ],
    )
    submit = SubmitField("Submit Ticket")


class TicketUpdateForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[
            ("Open", "Open"),
            ("In Progress", "In Progress"),
            ("Resolved", "Resolved"),
            ("Closed", "Closed"),
        ],
        validators=[DataRequired()],
    )
    priority = SelectField(
        "Priority",
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High"), ("Critical", "Critical")],
        validators=[DataRequired()],
    )
    admin_remark = TextAreaField("Admin Remarks", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Update Ticket")
