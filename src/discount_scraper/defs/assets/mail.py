import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import dagster as dg
from discount_scraper.data.webprocessing_result import WebprocessingResult
from discount_scraper.user_input import get_list
from discount_scraper.constants import RECIPIENT_EMAILS_PATH
from discount_scraper.email_templates import (
    PARSING_ERROR_HTML_TEMPLATE,
    PARSING_ERROR_PLAIN_TEMPLATE,
)

RECIPIENT_MAIL_ADDRESSES = get_list(RECIPIENT_EMAILS_PATH)


@dg.op(
    name="mail_message",
    out=dg.Out(metadata={"result_type": "MIMEMultipart"}),
)
def mail_message(results: list[WebprocessingResult] | None) -> dg.Output:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Angebote der kommenden Woche"
    msg["From"] = os.getenv("SENDER_MAIL_ADDRESS")
    msg["To"] = ",".join(RECIPIENT_MAIL_ADDRESSES)

    if results is not None:
        # results is a list of all outputs from webscrape_store
        plain_text = WebprocessingResult.parse(results, "plain")
        html_text = WebprocessingResult.parse(results, "html")
    else:
        plain_text = PARSING_ERROR_PLAIN_TEMPLATE
        html_text = PARSING_ERROR_HTML_TEMPLATE

    plain_text_mime = MIMEText(plain_text, "plain")
    html_text_mime = MIMEText(html_text, "html")

    # Add plain text and html.
    # Html is added last and thus attempted to be rendered first.
    msg.attach(plain_text_mime)
    msg.attach(html_text_mime)

    return dg.Output(value=msg, metadata={"plain_text": plain_text, "html": html_text})


@dg.op(
    name="send_mail",
    out=dg.Out(metadata={"result_type": "Output"}),
)
def send_mail(mail_message: MIMEMultipart) -> dg.Output:
    sender = os.getenv("SENDER_MAIL_ADDRESS")
    smtp_server = os.getenv("SENDER_MAIL_SMTP_SERVER")
    msg_str = mail_message.as_string()

    ssl_context = ssl.create_default_context()
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3

    with smtplib.SMTP_SSL(smtp_server, 465, context=ssl_context) as mail_server:
        mail_server.login(sender, os.getenv("SENDER_MAIL_PASSWORD"))
        mail_server.sendmail(sender, RECIPIENT_MAIL_ADDRESSES, msg_str)

    return dg.Output(
        value=None,
        metadata={
            "sender": sender,
            "recipients": list(RECIPIENT_MAIL_ADDRESSES),
            "message_string": msg_str,
        },
    )
