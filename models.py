from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    users = db.relationship("User", back_populates="department")
    subjects = db.relationship("Subject", back_populates="department")

    def __repr__(self):
        return f"<Department {self.code}>"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student", index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id", ondelete="SET NULL"))
    study_year = db.Column(db.Integer)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    department = db.relationship("Department", back_populates="users")
    taught_subjects = db.relationship("Subject", back_populates="teacher", foreign_keys="Subject.teacher_id")
    enrollments = db.relationship("Enrollment", back_populates="student", cascade="all, delete-orphan", foreign_keys="Enrollment.student_id")
    attendance_items = db.relationship("AttendanceItem", back_populates="student", cascade="all, delete-orphan")
    leave_requests = db.relationship("LeaveRequest", back_populates="student", cascade="all, delete-orphan", foreign_keys="LeaveRequest.student_id")

    __table_args__ = (
        db.CheckConstraint("role IN ('admin', 'teacher', 'student')", name="ck_user_role"),
        db.CheckConstraint("status IN ('active', 'pending', 'inactive')", name="ck_user_status"),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Subject(db.Model):
    __tablename__ = "subject"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    code = db.Column(db.String(30), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id", ondelete="RESTRICT"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    study_year = db.Column(db.Integer, nullable=False, default=1)
    weekday = db.Column(db.String(9))
    start_time = db.Column(db.String(5))
    end_time = db.Column(db.String(5))
    room = db.Column(db.String(80))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    department = db.relationship("Department", back_populates="subjects")
    teacher = db.relationship("User", back_populates="taught_subjects", foreign_keys=[teacher_id])
    enrollments = db.relationship("Enrollment", back_populates="subject", cascade="all, delete-orphan")
    attendance_records = db.relationship("AttendanceRecord", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subject {self.code}>"


class Enrollment(db.Model):
    __tablename__ = "enrollment"
    student_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id", ondelete="CASCADE"), primary_key=True)
    enrolled_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    student = db.relationship("User", back_populates="enrollments", foreign_keys=[student_id])
    subject = db.relationship("Subject", back_populates="enrollments")


class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    session = db.Column(db.String(80), nullable=False, default="Regular")
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id", ondelete="CASCADE"), nullable=False, index=True)
    marked_by_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    subject = db.relationship("Subject", back_populates="attendance_records")
    marked_by = db.relationship("User", foreign_keys=[marked_by_id])
    items = db.relationship("AttendanceItem", back_populates="record", cascade="all, delete-orphan")

    __table_args__ = (db.UniqueConstraint("date", "session", "subject_id", name="uq_attendance_session"),)


class AttendanceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey("attendance_record.id", ondelete="CASCADE"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    remarks = db.Column(db.String(500), nullable=False, default="")

    record = db.relationship("AttendanceRecord", back_populates="items")
    student = db.relationship("User", back_populates="attendance_items")

    __table_args__ = (
        db.UniqueConstraint("record_id", "student_id", name="uq_attendance_item_student"),
        db.CheckConstraint("status IN ('present', 'absent', 'late', 'excused')", name="ck_attendance_status"),
    )


class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    reviewed_at = db.Column(db.DateTime(timezone=True))
    attachment_filename = db.Column(db.String(255))
    attachment_original_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    student = db.relationship("User", back_populates="leave_requests", foreign_keys=[student_id])
    reviewed_by = db.relationship("User", foreign_keys=[reviewed_by_id])

    __table_args__ = (
        db.CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="ck_leave_status"),
        db.CheckConstraint("end_date >= start_date", name="ck_leave_dates"),
    )


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(80), nullable=False)
    entity_id = db.Column(db.String(80))
    details = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    actor = db.relationship("User", foreign_keys=[actor_id])


class SystemSetting(db.Model):
    key = db.Column(db.String(80), primary_key=True)
    value = db.Column(db.String(255), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    updated_by = db.relationship("User", foreign_keys=[updated_by_id])
