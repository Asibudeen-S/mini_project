"""Create the demo admin, six department HODs, and three year batches."""

import os
from datetime import date, timedelta

from app import app
from extensions import db
from models import (AttendanceItem, AttendanceRecord, Department, Enrollment,
                    LeaveRequest, Subject, SystemSetting, User)


FIRST_NAMES = [
    "Aarav", "Ananya", "Arjun", "Diya", "Ishaan", "Kavya", "Rohan", "Saanvi", "Vikram", "Meera",
    "Aditya", "Aditi", "Kabir", "Myra", "Reyansh", "Ira", "Vivaan", "Sara", "Dhruv", "Tara",
    "Krishna", "Nisha", "Ritvik", "Pooja", "Devansh", "Tanvi", "Om", "Sneha", "Kunal", "Mira",
]

BRANCHES = {
    "ECE": {
        "name": "Electronics and Communication Engineering",
        "hod": ("Dr. Ananya Rao", "hod.ece@example.com"),
        "surnames": ["Iyer", "Reddy", "Nair", "Gupta", "Rao", "Singh", "Joshi"],
        "legacy_year1": [
            "Aarav Sharma", "Ananya Patel", "Arjun Kumar", "Diya Iyer", "Ishaan Reddy",
            "Kavya Nair", "Rohan Gupta", "Saanvi Rao", "Vikram Singh", "Meera Joshi",
        ],
        "subjects": {
            1: [("Basic Electrical Engineering", "Monday", "09:00", "10:00"), ("Digital Electronics", "Wednesday", "11:00", "12:00")],
            2: [("Signals and Systems", "Tuesday", "09:00", "10:00"), ("Analog Communication", "Thursday", "11:00", "12:00")],
            3: [("Embedded Systems", "Monday", "13:00", "14:00"), ("Antenna and Wave Propagation", "Friday", "10:00", "11:00")],
        },
    },
    "CS": {
        "name": "Computer Science",
        "hod": ("Prof. Arjun Mehta", "hod.cs@example.com"),
        "surnames": ["Verma", "Shah", "Malhotra", "Desai", "Mukherjee", "Chatterjee", "Menon"],
        "legacy_year1": [
            "Aditya Verma", "Aditi Shah", "Kabir Malhotra", "Myra Desai", "Reyansh Kapoor",
            "Ira Mukherjee", "Vivaan Chatterjee", "Sara Khan", "Dhruv Menon", "Tara Sinha",
        ],
        "subjects": {
            1: [("Programming Fundamentals", "Monday", "09:00", "10:00"), ("Computer Organization", "Wednesday", "11:00", "12:00")],
            2: [("Data Structures", "Tuesday", "09:00", "10:00"), ("Database Systems", "Thursday", "11:00", "12:00")],
            3: [("Operating Systems", "Monday", "13:00", "14:00"), ("Software Engineering", "Friday", "10:00", "11:00")],
        },
    },
    "MECH": {
        "name": "Mechanical Engineering",
        "hod": ("Dr. Kavita Nair", "hod.mech@example.com"),
        "surnames": ["Pillai", "Kulkarni", "Bose", "Shetty", "Yadav", "Banerjee", "Gowda"],
        "legacy_year1": [
            "Krishna Pillai", "Nisha Kulkarni", "Ritvik Bose", "Pooja Shetty", "Devansh Yadav",
            "Tanvi Banerjee", "Om Prakash", "Sneha Gowda", "Kunal Das", "Mira Thomas",
        ],
        "subjects": {
            1: [("Engineering Mechanics", "Monday", "09:00", "10:00"), ("Engineering Drawing", "Wednesday", "11:00", "12:00")],
            2: [("Thermodynamics", "Tuesday", "09:00", "10:00"), ("Fluid Mechanics", "Thursday", "11:00", "12:00")],
            3: [("Manufacturing Technology", "Monday", "13:00", "14:00"), ("Machine Design", "Friday", "10:00", "11:00")],
        },
    },
    "AERO": {
        "name": "Aeronautical Engineering",
        "hod": ("Prof. Vikram Menon", "hod.aero@example.com"),
        "surnames": ["Kapoor", "Saxena", "Rathore", "Chauhan", "Sengupta", "Bhat"],
        "subjects": {
            1: [("Introduction to Aeronautics", "Monday", "09:00", "10:00"), ("Engineering Mechanics", "Wednesday", "11:00", "12:00")],
            2: [("Aerodynamics", "Tuesday", "09:00", "10:00"), ("Aircraft Structures", "Thursday", "11:00", "12:00")],
            3: [("Aircraft Propulsion", "Monday", "13:00", "14:00"), ("Flight Dynamics", "Friday", "10:00", "11:00")],
        },
    },
    "SE": {
        "name": "Software Engineering",
        "hod": ("Dr. Neha Kapoor", "hod.se@example.com"),
        "surnames": ["Agarwal", "Bhatt", "Srinivasan", "Mishra", "Trivedi", "Naidu"],
        "subjects": {
            1: [("Software Foundations", "Monday", "09:00", "10:00"), ("Discrete Mathematics", "Wednesday", "11:00", "12:00")],
            2: [("Algorithms", "Tuesday", "09:00", "10:00"), ("Web Engineering", "Thursday", "11:00", "12:00")],
            3: [("Software Architecture", "Monday", "13:00", "14:00"), ("Testing and Quality Assurance", "Friday", "10:00", "11:00")],
        },
    },
    "EEE": {
        "name": "Electrical and Electronics Engineering",
        "hod": ("Prof. Suresh Iyer", "hod.eee@example.com"),
        "surnames": ["Jain", "Patil", "Dutta", "Tiwari", "Bansal", "Sood"],
        "subjects": {
            1: [("Circuit Theory", "Monday", "09:00", "10:00"), ("Electrical Measurements", "Wednesday", "11:00", "12:00")],
            2: [("Electrical Machines", "Tuesday", "09:00", "10:00"), ("Power Systems", "Thursday", "11:00", "12:00")],
            3: [("Control Systems", "Monday", "13:00", "14:00"), ("Power Electronics", "Friday", "10:00", "11:00")],
        },
    },
}


def get_or_create_user(email, name, role, department, password=None, study_year=None):
    user = User.query.filter_by(email=email).first()
    if user is None:
        if not password:
            raise ValueError(f"A password is required when creating the demo account {email}.")
        user = User(name=name, email=email, role=role, status="active", department=department,
                    study_year=study_year)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
    else:
        user.name = name
        user.role = role
        user.status = "active"
        user.department = department
        user.study_year = study_year
        if password:
            user.set_password(password)
    return user


def seed():
    db.create_all()
    configured_admin_password = os.getenv("SEED_ADMIN_PASSWORD")
    hod_password = os.getenv("SEED_DEMO_PASSWORD", "DemoPassword123!")
    student_password = os.getenv("SEED_STUDENT_PASSWORD", "StudentDemo123!")

    extra_admin = User.query.filter(User.role == "admin", User.email != "admin@example.com").first()
    if extra_admin:
        raise RuntimeError("More than one admin role exists. Resolve the duplicate before seeding demo data.")

    departments = {}
    for code, spec in BRANCHES.items():
        department = Department.query.filter_by(code=code).first()
        if department is None:
            department = Department(name=spec["name"], code=code)
            db.session.add(department)
        else:
            department.name = spec["name"]
        departments[code] = department
    db.session.flush()

    # Preserve the original class records while making the course code match its year batch.
    for old_code, new_code in (("ECE202", "ECE102"), ("CS202", "CS102"), ("MECH202", "MECH102")):
        old_subject = Subject.query.filter_by(code=old_code).first()
        if old_subject and not Subject.query.filter_by(code=new_code).first():
            old_subject.code = new_code
    db.session.flush()

    admin = User.query.filter_by(email="admin@example.com").first()
    admin_already_exists = admin is not None
    if admin is None and User.query.filter_by(role="admin").first():
        raise RuntimeError("An admin account already exists under another email; seed will not create a second one.")
    admin_password = None if admin else (configured_admin_password or "ChangeThisBeforeDeploying123!")
    admin = get_or_create_user("admin@example.com", "Avery Morgan", "admin", None, admin_password)

    hods = {}
    students_by_batch = {}
    for code, spec in BRANCHES.items():
        hod_name, hod_email = spec["hod"]
        hods[code] = get_or_create_user(hod_email, hod_name, "teacher", departments[code], hod_password)
        for year in (1, 2, 3):
            students = []
            names = spec.get("legacy_year1") if year == 1 else None
            if names is None:
                offset = (year - 1) * 10
                names = [f"{FIRST_NAMES[offset + i]} {spec['surnames'][(i + year - 1) % len(spec['surnames'])]}"
                         for i in range(10)]
            for index, name in enumerate(names, start=1):
                email = (f"{code.lower()}.student{index:02d}@example.com" if year == 1
                         else f"{code.lower()}.year{year}.student{index:02d}@example.com")
                students.append(get_or_create_user(email, name, "student", departments[code],
                                                   student_password, study_year=year))
            students_by_batch[(code, year)] = students
        student_count = User.query.filter_by(role="student", department_id=departments[code].id).filter(
            User.status.in_(["active", "pending"])).count()
        if student_count > 100:
            raise RuntimeError(f"{spec['name']} has {student_count} student records; the limit is 100.")
    db.session.flush()

    subjects = []
    for code, spec in BRANCHES.items():
        for year, course_list in spec["subjects"].items():
            for course_number, (name, weekday, start_time, end_time) in enumerate(course_list, start=1):
                subject_code = f"{code}{year}{course_number:02d}"
                subject = Subject.query.filter_by(code=subject_code).first()
                if subject is None:
                    subject = Subject(name=name, code=subject_code, department=departments[code],
                                      teacher=hods[code], study_year=year)
                    db.session.add(subject)
                subject.name = name
                subject.department = departments[code]
                subject.teacher = hods[code]
                subject.study_year = year
                subject.weekday = weekday
                subject.start_time = start_time
                subject.end_time = end_time
                subject.room = f"{code}-{year}{course_number:02d}"
                db.session.flush()
                subjects.append(subject)
                for student in students_by_batch[(code, year)]:
                    if db.session.get(Enrollment, (student.id, subject.id)) is None:
                        db.session.add(Enrollment(student_id=student.id, subject_id=subject.id))
    db.session.flush()

    class_dates = []
    cursor = date.today() - timedelta(days=34)
    while cursor <= date.today():
        if cursor.weekday() < 5:
            class_dates.append(cursor)
        cursor += timedelta(days=1)
    for subject_index, subject in enumerate(subjects):
        roster = [enrollment.student for enrollment in subject.enrollments]
        marked_by = hods[subject.department.code]
        for day_index, class_date in enumerate(class_dates[-20:]):
            record = AttendanceRecord.query.filter_by(subject_id=subject.id, date=class_date,
                                                      session="Morning").first()
            if record is None:
                record = AttendanceRecord(subject_id=subject.id, date=class_date,
                                          session="Morning", marked_by=marked_by)
                db.session.add(record)
                db.session.flush()
            for student in roster:
                item = AttendanceItem.query.filter_by(record_id=record.id, student_id=student.id).first()
                value = (day_index * 3 + student.id + subject_index * 5) % 17
                status = "absent" if value in {0, 1, 2} else "late" if value in {5, 11} else "excused" if value == 9 else "present"
                if item is None:
                    db.session.add(AttendanceItem(record_id=record.id, student_id=student.id, status=status))
                else:
                    item.status = status

    first_student = students_by_batch[("ECE", 1)][0]
    if not LeaveRequest.query.filter_by(student_id=first_student.id, reason="Medical appointment").first():
        db.session.add(LeaveRequest(student_id=first_student.id,
                                    start_date=date.today() + timedelta(days=7),
                                    end_date=date.today() + timedelta(days=7),
                                    reason="Medical appointment", status="pending"))
    setting = db.session.get(SystemSetting, "attendance_threshold")
    if setting is None:
        db.session.add(SystemSetting(key="attendance_threshold", value="75", updated_by=admin))
    db.session.commit()

    print("Demo data is ready: one admin, six department HODs, 18 year batches, and 180 students.")
    print("Admin: admin@example.com")
    print("HOD emails: " + ", ".join(spec["hod"][1] for spec in BRANCHES.values()))
    if admin_already_exists:
        print("Existing admin password preserved.")
    elif configured_admin_password:
        print("Admin password set from SEED_ADMIN_PASSWORD (value omitted).")
    else:
        print("Default admin password: ChangeThisBeforeDeploying123!")
    print("Student demo password: StudentDemo123!" if not os.getenv("SEED_STUDENT_PASSWORD")
          else "Student passwords set from SEED_STUDENT_PASSWORD (value omitted).")
    print("Student emails use <branch>.student01@example.com for Year 1 and <branch>.year2/year3.student01@example.com for Years 2 and 3.")
    print("Change demo passwords before using the seeded database beyond local development.")


if __name__ == "__main__":
    with app.app_context():
        seed()
