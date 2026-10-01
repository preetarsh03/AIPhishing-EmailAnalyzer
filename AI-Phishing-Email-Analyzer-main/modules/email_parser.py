from email import policy
from email.parser import BytesParser
import re


def parse_email(file_path):

    with open(file_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    sender = msg.get("From")
    receiver = msg.get("To")
    subject = msg.get("Subject")
    date = msg.get("Date")

    body = ""

    if msg.is_multipart():

        for part in msg.walk():

            if part.get_content_type() == "text/plain":

                try:
                    body += part.get_content()
                except:
                    pass

    else:

        try:
            body = msg.get_content()
        except:
            body = ""

    # Extract URLs
    urls = re.findall(r'https?://[^\s]+', body)

    # Extract Attachments
    attachments = []

    for part in msg.iter_attachments():

        filename = part.get_filename()

        if filename:

            attachments.append(filename)

    return {

        "sender": sender,

        "receiver": receiver,

        "subject": subject,

        "date": date,

        "body": body,

        "urls": urls,

        "attachments": attachments
    }