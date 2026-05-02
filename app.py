from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
import json

app = Flask(__name__)
app.secret_key = "mjpru_2026_key"


def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="mjpru_advance_db"
    )


# ============================================
# PUBLIC PAGES (NO LOGIN REQUIRED)
# ============================================


@app.route("/")
def home():
    """Landing page with college info"""
    return render_template("home.html")


@app.route("/public/students")
def public_students():
    """Public view of students - No login required"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.s_id, s.name, h.h_name, d.d_name, s.city 
        FROM students s
        LEFT JOIN hostels h ON s.h_id = h.h_id
        LEFT JOIN departments d ON s.d_id = d.d_id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    cols = ["ID", "Student Name", "Hostel", "Department", "City"]
    return render_template(
        "public_data.html",
        data=data,
        columns=cols,
        title="Students",
    )


@app.route("/public/faculty")
def public_faculty():
    """Public view of faculty - No login required"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT f.f_name, f.designation, f.qualifications, f.specialization, d.d_name
        FROM faculty f
        LEFT JOIN departments d ON f.d_id = d.d_id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    cols = ["Name", "Designation", "Qualifications", "Specialization", "Department"]
    return render_template(
        "public_data.html",
        data=data,
        columns=cols,
        title="Faculty",
    )


@app.route("/public/library")
def public_library():
    """Public view of library - No login required"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT l.book_id, l.book_name, l.author, l.status, IFNULL(s.name, 'Available')
        FROM library l 
        LEFT JOIN students s ON l.s_id = s.s_id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    cols = ["ID", "Book Name", "Author", "Status", "Issued To"]
    return render_template(
        "public_data.html",
        data=data,
        columns=cols,
        title="Library",
    )


@app.route("/public/departments")
def public_departments():
    """Public view of departments - No login required"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT d.d_id, d.d_name, COUNT(s.s_id) as total_students
        FROM departments d
        LEFT JOIN students s ON d.d_id = s.d_id
        GROUP BY d.d_id, d.d_name
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    cols = ["ID", "Department Name", "Total Students"]
    return render_template(
        "public_data.html",
        data=data,
        columns=cols,
        title="Departments",
    )


@app.route("/public/hostels")
def public_hostels():
    """Public view of hostels - No login required"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT h_id, h_name, no_of_seats FROM hostels")
    data = cursor.fetchall()
    conn.close()
    cols = ["ID", "Hostel Name", "Seats"]
    return render_template(
        "public_data.html",
        data=data,
        columns=cols,
        title="Hostels",
    )


# ============================================
# ADMIN ROUTES (LOGIN REQUIRED)
# ============================================


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page"""
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")

        # Admin credentials check
        if user == "kuldeep" and pw == "curios_123":
            session["logged_in"] = True
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template(
                "admin_login.html", error="Invalid username or password!"
            )

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect(url_for("home"))


@app.route("/admin/dashboard")
def admin_dashboard():
    """Admin dashboard - Protected"""
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM faculty")
    total_faculty = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM library")
    total_books = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_faculty=total_faculty,
        total_books=total_books,
    )


# ============================================
# ADMIN DATA MANAGEMENT PAGES
# ============================================


@app.route("/admin/students")
def admin_students():
    """Admin view of students - Protected"""
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.s_id, s.name, h.h_name, d.d_name, s.city 
        FROM students s
        LEFT JOIN hostels h ON s.h_id = h.h_id
        LEFT JOIN departments d ON s.d_id = d.d_id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    cols = ["ID", "Student Name", "Hostel", "Department", "City"]
    return render_template(
        "admin_data.html", data=data, columns=cols, title="Manage Students"
    )


@app.route("/admin/faculty")
def admin_faculty():
    """Admin view of faculty - Protected"""
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT f.f_id, f.f_name, f.designation, f.qualifications, f.specialization, d.d_name
        FROM faculty f
        LEFT JOIN departments d ON f.d_id = d.d_id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    cols = [
        "ID",
        "Name",
        "Designation",
        "Qualifications",
        "Specialization",
        "Department",
    ]
    return render_template(
        "admin_data.html", data=data, columns=cols, title="Manage Faculty"
    )


@app.route("/admin/library")
def admin_library():
    """Admin view of library - Protected"""
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT l.book_id, l.book_name, l.author, l.status, IFNULL(s.name, 'Available')
        FROM library l 
        LEFT JOIN students s ON l.s_id = s.s_id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    cols = ["ID", "Book Name", "Author", "Status", "Issued To"]
    return render_template(
        "admin_data.html", data=data, columns=cols, title="Manage Library"
    )


# ============================================
# LEGACY ROUTES (For backwards compatibility)
# ============================================


@app.route("/login", methods=["GET", "POST"])
def login():
    """Redirect to admin login"""
    return redirect(url_for("admin_login"))


@app.route("/logout")
def logout():
    """Redirect to admin logout"""
    return redirect(url_for("admin_logout"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
