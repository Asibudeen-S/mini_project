from datetime import date

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (DateField, PasswordField, SelectField, SelectMultipleField,
                     StringField, SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length, Optional,
                                Regexp, ValidationError)


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class DepartmentForm(FlaskForm):
    name = StringField("Department name", validators=[DataRequired(), Length(max=120)])
    code = StringField("Code", validators=[DataRequired(), Length(max=20), Regexp(r"^[A-Za-z0-9_-]+$", message="Use letters, numbers, hyphens or underscores.")])
    submit = SubmitField("Save department")


class SubjectForm(FlaskForm):
    name = StringField("Class / subject name", validators=[DataRequired(), Length(max=140)])
    code = StringField("Class code", validators=[DataRequired(), Length(max=30), Regexp(r"^[A-Za-z0-9_-]+$", message="Use letters, numbers, hyphens or underscores.")])
    department_id = SelectField("Department", coerce=int, validators=[DataRequired()])
    study_year = SelectField("Year batch", coerce=int, choices=[(1, "Year 1"), (2, "Year 2"), (3, "Year 3")], validators=[DataRequired()])
    teacher_id = SelectField("Assigned HOD", coerce=int, validators=[Optional()])
    weekday = SelectField("Day", choices=[(day, day) for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")], validators=[DataRequired()])
    start_time = StringField("Starts at (24-hour HH:MM)", validators=[DataRequired(), Regexp(r"^([01][0-9]|2[0-3]):[0-5][0-9]$", message="Use 24-hour HH:MM time.")])
    end_time = StringField("Ends at (24-hour HH:MM)", validators=[DataRequired(), Regexp(r"^([01][0-9]|2[0-3]):[0-5][0-9]$", message="Use 24-hour HH:MM time.")])
    room = StringField("Room", validators=[Optional(), Length(max=80)])
    student_ids = SelectMultipleField("Enrolled students", coerce=int, validators=[Optional()])
    submit = SubmitField("Save class")


class UserAdminForm(FlaskForm):
    role = SelectField("Role", choices=[("admin", "Administrator"), ("teacher", "Department HOD"), ("student", "Student record")], validators=[DataRequired()])
    status = SelectField("Account status", choices=[("active", "Active"), ("pending", "Pending"), ("inactive", "Inactive")], validators=[DataRequired()])
    department_id = SelectField("Department", coerce=int, validators=[Optional()])
    study_year = SelectField("Study year", coerce=int, choices=[(0, "Not applicable"), (1, "Year 1"), (2, "Year 2"), (3, "Year 3")], validators=[Optional()])
    new_password = PasswordField("Set a new password (optional)", validators=[Optional(), Length(min=10, max=128)])
    submit = SubmitField("Update account")


class AdminCreateUserForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    role = SelectField("Role", choices=[("teacher", "Department HOD"), ("student", "Student")], validators=[DataRequired()])
    status = SelectField("Account status", choices=[("active", "Active"), ("pending", "Pending")], validators=[DataRequired()])
    department_id = SelectField("Department", coerce=int, validators=[Optional()])
    study_year = SelectField("Study year", coerce=int, choices=[(0, "Select year"), (1, "Year 1"), (2, "Year 2"), (3, "Year 3")], validators=[Optional()])
    password = PasswordField("Temporary password", validators=[DataRequired(), Length(min=10, max=128)])
    submit = SubmitField("Create account")


class AttendanceSelectorForm(FlaskForm):
    subject_id = SelectField("Class", coerce=int, validators=[DataRequired()])
    date = DateField("Date", default=date.today, validators=[DataRequired()])
    session = StringField("Session", default="Regular", validators=[DataRequired(), Length(max=80)])
    submit = SubmitField("Open marking sheet")


class LeaveRequestForm(FlaskForm):
    start_date = DateField("Start date", validators=[DataRequired()])
    end_date = DateField("End date", validators=[DataRequired()])
    reason = TextAreaField("Reason", validators=[DataRequired(), Length(min=10, max=3000)])
    attachment = FileField("Supporting document (optional)", validators=[Optional()])
    submit = SubmitField("Submit request")

    def validate_end_date(self, field):
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError("End date must be on or after the start date.")


class ReviewLeaveForm(FlaskForm):
    status = SelectField("Decision", choices=[("approved", "Approve"), ("rejected", "Reject")], validators=[DataRequired()])
    submit = SubmitField("Save decision")


class ProfileForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    current_password = PasswordField("Current password", validators=[Optional()])
    new_password = PasswordField("New password", validators=[Optional(), Length(min=10, max=128)])
    confirm_password = PasswordField("Confirm new password", validators=[Optional(), EqualTo("new_password")])
    submit = SubmitField("Save profile")


class SettingsForm(FlaskForm):
    attendance_threshold = StringField("Low attendance threshold (%)", validators=[DataRequired(), Regexp(r"^(100(?:\.0{1,2})?|(?:[0-9]|[1-9][0-9])(?:\.[0-9]{1,2})?)$", message="Enter a percentage from 0 to 100.")])
    submit = SubmitField("Save settings")
