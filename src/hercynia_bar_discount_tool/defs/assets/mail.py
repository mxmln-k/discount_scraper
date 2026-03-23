import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import dagster as dg
from hercynia_bar_discount_tool.user_input import get_mail_addresses
from hercynia_bar_discount_tool.constants import RECIPIENT_EMAILS_PATH
from hercynia_bar_discount_tool.defs.assets.webscraper import WEBSCRAPE_ASSETS
from hercynia_bar_discount_tool.helpers import parse

__GROUP_NAME__ = "mail"
RECIPIENT_MAIL_ADDRESSES = get_mail_addresses(RECIPIENT_EMAILS_PATH)


@dg.asset(
    group_name=__GROUP_NAME__,
    ins={asset.key.path[-1]: dg.AssetIn(asset.key) for asset in WEBSCRAPE_ASSETS},
)
def mail_message(**upstream_values) -> dg.MaterializeResult:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Angebote der kommenden Woche"
    msg["From"] = os.getenv("SENDER_MAIL_ADDRESS")
    msg["To"] = ",".join(RECIPIENT_MAIL_ADDRESSES)

    upstream_values = list(upstream_values.values())
    plain_text = parse(upstream_values, "plain")
    html_text = parse(upstream_values, "html")

    plain_text_mime = MIMEText(plain_text, "plain")
    html_text_mime = MIMEText(html_text, "html")

    # Add plain text and html.
    # Html is added last and thus attempted to be rendered first.
    msg.attach(plain_text_mime)
    msg.attach(html_text_mime)

    return dg.MaterializeResult(
        value=msg, metadata={"plain_text": plain_text, "html": html_text}
    )


@dg.asset(
    group_name=__GROUP_NAME__,
    deps=[mail_message],
)
def send_mail(mail_message: MIMEMultipart) -> dg.MaterializeResult:
    sender = os.getenv("SENDER_MAIL_ADDRESS")
    smtp_server = os.getenv("SENDER_MAIL_SMTP_SERVER")
    msg_str = mail_message.as_string()

    ssl_context = ssl.create_default_context()
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3

    with smtplib.SMTP_SSL(smtp_server, 465, context=ssl_context) as mail_server:
        mail_server.login(sender, os.getenv("SENDER_MAIL_PASSWORD"))
        mail_server.sendmail(sender, RECIPIENT_MAIL_ADDRESSES, msg_str)

    return dg.MaterializeResult(
        metadata={
            "sender": sender,
            "recipients": list(RECIPIENT_MAIL_ADDRESSES),
            "message_string": msg_str,
        }
    )
