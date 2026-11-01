SUSPICIOUS_KEYWORDS = [
    "urgent",
    "verify",
    "password",
    "account",
    "bank",
    "payment",
    "invoice",
    "click",
    "login",
    "security",
    "confirm",
    "immediately",
    "suspended",
    "expire",
    "winner",
    "lottery"
]


def analyze_email(email_data):

    score = 0
    findings = []

    # --------------------
    # Subject Analysis
    # --------------------

    subject = (email_data["subject"] or "").lower()

    for word in SUSPICIOUS_KEYWORDS:

        if word in subject:
            score += 5
            findings.append(f"Subject contains '{word}'")

    # --------------------
    # Body Analysis
    # --------------------

    body = (email_data["body"] or "").lower()

    for word in SUSPICIOUS_KEYWORDS:

        if word in body:
            score += 3
            findings.append(f"Body contains '{word}'")

    # --------------------
    # URL Analysis
    # --------------------

    urls = email_data.get("urls", email_data.get("links", []))

    if len(urls):

        score += 10
        findings.append("Email contains URL")

    for url in urls:

        if url.startswith("http://"):
            score += 10
            findings.append("Uses HTTP")

        if ".xyz" in url:
            score += 10
            findings.append("Suspicious .xyz domain")

        if "bit.ly" in url:
            score += 10
            findings.append("Shortened URL")

    # --------------------
    # Final Verdict
    # --------------------

    if score >= 60:
        verdict = "PHISHING"

    elif score >= 30:
        verdict = "SUSPICIOUS"

    else:
        verdict = "SAFE"

    return {

        "score": score,

        "verdict": verdict,

        "findings": findings

    }