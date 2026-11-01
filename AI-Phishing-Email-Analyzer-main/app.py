from flask import Flask, render_template, request
from modules.email_parser import parse_email
from modules.rule_engine import analyze_email
import os
import sqlite3
import re
from email import policy

app = Flask(__name__)

# -----------------------------------
# Configuration
# -----------------------------------

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "AIPhishingAnalyzer2026"

# Create Upload Folder Automatically
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------------
# Database Setup
# -----------------------------------

DATABASE = "email_history.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verdict TEXT NOT NULL,
            score REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------------
# Routes
# -----------------------------------

def save_email_result(result):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO email_history (verdict, score) VALUES (?, ?)",
        (result["verdict"], result["score"])
    )

    conn.commit()
    conn.close()

@app.route("/")
def login():
    return render_template("login.html")



@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM email_history")
    total_emails = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM email_history WHERE verdict = 'SAFE'"
    )
    safe_emails = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM email_history WHERE verdict = 'PHISHING'"
    )
    phishing_emails = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(score) FROM email_history")
    average_score = cursor.fetchone()[0] or 0

    conn.close()

    risk_score = min(round(average_score), 100)

    return render_template(
        "dashboard.html",
        total_emails=total_emails,
        safe_emails=safe_emails,
        phishing_emails=phishing_emails,
        risk_score=risk_score
    )


@app.route("/analyze")
def analyze():
    return render_template("analyze.html")


@app.route("/analyze-email", methods=["POST"])
def analyze_email_route():

    uploaded_file = request.files.get("email_file")
    email_text = request.form.get("email_text")

    # -------------------------------
    # Upload .EML File
    # -------------------------------

    if uploaded_file and uploaded_file.filename != "":

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            uploaded_file.filename
        )

        uploaded_file.save(filepath)

        # Parse Email
        email_data = parse_email(filepath)

        # Rule Engine Analysis
        result = analyze_email(email_data)
        save_email_result(result)
        return render_template(
            "report.html",
            email_data=email_data,
            result=result
        )

    # -------------------------------
    # Paste Email
    # -------------------------------

    
    elif email_text and email_text.strip():

        
        from email.parser import Parser

        parsed_email = Parser(policy=policy.default).parsestr(email_text)

        # Extract URLs from pasted email
        links = re.findall(
            r'https?://[^\s<>"\']+|www\.[^\s<>"\']+',
            email_text
        )

        email_data = {
            "body": email_text,
            "sender": str(parsed_email.get("From", "security@example.com")),
            "recipient": str(parsed_email.get("To", "user@example.com")),
            "subject": str(parsed_email.get("Subject", "Urgent Account Verification")),
            "date": str(parsed_email.get("Date", "Sat, 31 Oct 2026 10:00:00")),
            "links": links,
            "urls": links,
            "attachments": []
        }

        result = analyze_email(email_data)
        save_email_result(result)
        return render_template(
            "report.html",
            email_data=email_data,
            result=result
        )

    else:

        return """
        <h2>No Email Uploaded!</h2>
        <br>
        <a href='/analyze'>Go Back</a>
        """

# -----------------------------------
# Run Application
# -----------------------------------

if __name__ == "__main__":
    app.run(debug=True)