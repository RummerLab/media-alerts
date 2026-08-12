from __future__ import annotations

import logging
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

from .config import MAIL_CC, MAIL_FROM, MAIL_TO, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER
from .models import Article

logger = logging.getLogger(__name__)


def _plain_body(articles: list[Article]) -> str:
    lines = [
        f"=== News - {len(articles)} new result{'s' if len(articles) != 1 else ''} ===",
        "",
    ]
    for article in articles:
        lines.append(article.title)
        lines.append(f"- {article.source}")
        if article.snippet:
            lines.append(article.snippet)
        lines.append(article.url)
        lines.append("")
        lines.append("-" * 40)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _html_body(articles: list[Article]) -> str:
    items = []
    for article in articles:
        snippet = f"<p>{escape(article.snippet)}</p>" if article.snippet else ""
        items.append(
            "<div style='margin:0 0 24px 0;padding:0 0 16px 0;border-bottom:1px solid #e0e0e0'>"
            f"<p style='margin:0 0 4px 0'><strong>"
            f"<a href='{escape(article.url, quote=True)}'>{escape(article.title)}</a>"
            "</strong></p>"
            f"<p style='margin:0 0 8px 0;color:#666'>{escape(article.source)}"
            f" · {escape(article.feed)}</p>"
            f"{snippet}"
            "</div>"
        )
    joined = "".join(items)
    return (
        "<div style='font-family:Arial,sans-serif;max-width:640px;color:#222'>"
        f"<p><strong>News — {len(articles)} new "
        f"result{'s' if len(articles) != 1 else ''}</strong></p>"
        f"{joined}"
        "<p style='color:#888;font-size:12px'>RummerLab media digest · "
        "Google News, Bing, The Conversation, optional Guardian/NewsAPI</p>"
        "</div>"
    )


def send_digest(articles: list[Article]) -> None:
    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("SMTP_USER and SMTP_PASSWORD are required to send email")
    if not MAIL_TO:
        raise RuntimeError("MAIL_TO is empty")

    today = date.today().isoformat()
    subject = f"RummerLab media digest — {len(articles)} new result{'s' if len(articles) != 1 else ''} ({today})"
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = MAIL_FROM or SMTP_USER
    message["To"] = ", ".join(MAIL_TO)
    if MAIL_CC:
        message["Cc"] = ", ".join(MAIL_CC)
    message.attach(MIMEText(_plain_body(articles), "plain", "utf-8"))
    message.attach(MIMEText(_html_body(articles), "html", "utf-8"))

    recipients = [*MAIL_TO, *MAIL_CC]
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.sendmail(MAIL_FROM or SMTP_USER, recipients, message.as_string())
    logger.info("Sent digest to %s", recipients)
