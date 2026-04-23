from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "data.db")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "nirbhay_tyagi_2026_secure_key"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    if os.path.exists(DB_PATH):
        return

    connection = get_db()
    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL
        );

        CREATE TABLE results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course TEXT NOT NULL,
            semester TEXT NOT NULL,
            marks INTEGER NOT NULL,
            grade TEXT NOT NULL,
            remarks TEXT,
            FOREIGN KEY(student_id) REFERENCES users(id)
        );
        """
    )

    cursor.execute(
        "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
        ("admin", generate_password_hash("admin123"), "admin", "Campus Admin"),
    )

    cursor.execute(
        "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
        ("student", generate_password_hash("student123"), "student", "Riya Sharma"),
    )

    connection.commit()
    connection.close()


def setup_database():
    init_db()


def compute_grade(marks):
    if marks >= 90:
        return "A+"
    if marks >= 80:
        return "A"
    if marks >= 70:
        return "B+"
    if marks >= 60:
        return "B"
    if marks >= 50:
        return "C"
    return "F"


@app.route("/")
def home():
    setup_database()
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    setup_database()

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        connection = get_db()
        user = connection.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        connection.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["full_name"] = user["full_name"]
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if session.get("role") == "admin":
        connection = get_db()
        students = connection.execute(
            "SELECT id, username, full_name FROM users WHERE role = 'student'"
        ).fetchall()
        connection.close()
        return render_template("admin_dashboard.html", students=students)

    connection = get_db()
    results = connection.execute(
        "SELECT * FROM results WHERE student_id = ? ORDER BY semester, course",
        (session["user_id"],),
    ).fetchall()
    connection.close()

    return render_template("student_dashboard.html", results=results)


@app.route("/upload", methods=["GET", "POST"])
def upload_result():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    connection = get_db()
    students = connection.execute(
        "SELECT id, full_name FROM users WHERE role = 'student'"
    ).fetchall()

    if request.method == "POST":
        student_id = request.form.get("student_id")
        course = request.form.get("course", "").strip()
        semester = request.form.get("semester", "").strip()
        marks = request.form.get("marks", "").strip()
        remarks = request.form.get("remarks", "").strip()

        if not student_id or not course or not semester or not marks.isdigit():
            flash("Please fill in all required fields with valid values.", "error")
            connection.close()
            return render_template("upload_results.html", students=students)

        marks_value = int(marks)
        grade = compute_grade(marks_value)

        connection.execute(
            """
            INSERT INTO results
            (student_id, course, semester, marks, grade, remarks)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (student_id, course, semester, marks_value, grade, remarks),
        )

        connection.commit()
        connection.close()

        flash("Result uploaded successfully.", "success")
        return redirect(url_for("dashboard"))

    connection.close()
    return render_template("upload_results.html", students=students)


@app.route("/student/<int:student_id>")
def student_profile(student_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    connection = get_db()

    student = connection.execute(
        """
        SELECT id, username, full_name
        FROM users
        WHERE id = ? AND role = 'student'
        """,
        (student_id,),
    ).fetchone()

    results = connection.execute(
        """
        SELECT *
        FROM results
        WHERE student_id = ?
        ORDER BY semester, course
        """,
        (student_id,),
    ).fetchall()

    connection.close()

    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("dashboard"))

    return render_template(
        "view_results.html",
        student=student,
        results=results
    )


if __name__ == "__main__":
    setup_database()
    app.run(debug=False)