# Student Result Management System

A small Flask web application for managing student results with secure login, admin upload, and student result viewing.

## Features

- Admin and student login
- Admin dashboard to upload and review student results
- Student dashboard to view personal grades
- Elegant and gentle UI with clean modern styling
- SQLite database for easy local setup

## Setup

1. Create a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
python app.py
```

4. Open in browser:

`http://127.0.0.1:5000`

## Default users

- Admin: `admin` / `admin123`
- Student: `student` / `student123`

## Notes

- The database file `data.db` is created automatically on first run.
- Change `app.secret_key` in `app.py` for a production-ready secret.
