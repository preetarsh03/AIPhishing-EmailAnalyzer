from flask import Flask, render_template, request
from modules.email_parser import parse_email
from modules.rule_engine import analyze_email
import os

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
# Routes
# -----------------------------------

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


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

        return render_template(
            "report.html",
            email_data=email_data,
            result=result
        )

    # -------------------------------
    # Paste Email
    # -------------------------------

    elif email_text and email_text.strip():

        return f"""
        <h2>Email Text Received</h2>

        <pre>{email_text}</pre>

        <br>

        <a href='/analyze'>Go Back</a>
        """

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