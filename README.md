# Attendance Hub

A role-based attendance management application built with Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, and SQLite. MySQL can be selected with a SQLAlchemy connection URL.

## Features

- **Single administrator:** overall access to accounts, departments, batches, classes, enrollment, attendance, reports, settings, and audit logs.
- **Department HODs:** one login per branch, scoped to their own students and classes for attendance, leave review, alerts, and reports.
- **Student logins:** students can see their attendance percentages and history, submit and track leave requests, view their year-wise timetable, and update their profile.
- **Six branches:** ECE, Computer Science, Mechanical, Aeronautical, Software Engineering, and EEE.
- **Three year batches per branch:** Year 1, Year 2, and Year 3. The demo creates 10 students per batch (30 per branch), within the 100-student limit per branch.
- **Security:** password hashing, CSRF protection, role checks, private attachment storage, upload limits, and HTTP-only session cookies.

Attendance percentages count Present and Late as attended and exclude Excused sessions. The default low-attendance threshold is 75%; the administrator can change it in Settings.

## Run locally

Use Python 3.10 or newer.

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 seed.py
python3 app.py
```

Open `http://127.0.0.1:5000`. Admin and HOD demo credentials are:

- Admin: `admin@example.com` / `ChangeThisBeforeDeploying123!`
- HOD emails: `hod.ece@example.com`, `hod.cs@example.com`, `hod.mech@example.com`, `hod.aero@example.com`, `hod.se@example.com`, `hod.eee@example.com` (each uses `DemoPassword123!`)
- Seeded student email examples: `ece.student01@example.com` (Year 1), `ece.year2.student01@example.com`, and `ece.year3.student01@example.com` (each uses `StudentDemo123!`)

Change demo passwords before using the seeded database beyond local development. Set `SEED_ADMIN_PASSWORD`, `SEED_DEMO_PASSWORD`, and `SEED_STUDENT_PASSWORD` in `.env` before running the seed script to choose local demo passwords. Re-running the seed preserves an existing admin password. If it is unknown, set a new one with `flask --app app reset-admin-password`.

The administrator creates and activates student accounts from User Accounts. Students must have a department, year batch, active status, and password before they can sign in. Self-registration is disabled.

For a clean installation without demo records, run `flask --app app create-admin` to create the first administrator, then create departments, HODs, and student accounts from the admin interface.

## Configuration

Copy `.env.example` to `.env` and set a long, random `SECRET_KEY`. `DATABASE_URL` defaults to `sqlite:///attendance.db` (stored under Flask's `instance/` directory). For MySQL, use a URL such as:

```text
DATABASE_URL=mysql+pymysql://attendance_user:password@db-host/attendance
```

Set `COOKIE_SECURE=1` when serving over HTTPS. Set `FLASK_DEBUG=1` only for local development. Keep `.env`, the `instance/` directory, and uploaded leave documents private, and put the app behind a production WSGI server and HTTPS reverse proxy.

If `SECRET_KEY` is not set, the app creates a private `instance/.secret_key` file and reuses it across app restarts and workers. The app adds the year and timetable columns to existing SQLite/MySQL databases during startup. Back up the database and `instance/uploads/` directory before upgrading.

## Project layout

```text
app.py                 Flask application factory, configuration, and CLI
extensions.py          Shared Flask-SQLAlchemy, Flask-Login, and CSRF extensions
models.py              SQLAlchemy models and relationships
forms.py               Validated Flask-WTF forms
routes.py              Authentication, RBAC, dashboards, workflows, reports
seed.py                Idempotent demo-data initializer
templates/             Jinja2 pages and shared layout
static/                Responsive CSS and attendance interactions
instance/              Local database and private uploads (created at runtime)
```
