import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings

logger = logging.getLogger(__name__)

_CC_ADDRESS = "hsuchen@g.ncu.edu.tw"


def _get_ses_client() -> Any:
    settings = get_settings()
    return boto3.client(
        "ses",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def send_verification_email(to_email: str, token: str) -> bool:
    settings = get_settings()
    verify_url = f"{settings.verify_base_url}/verify-email?token={token}"

    name, address = parseaddr(settings.email_from)
    from_formatted = formataddr((name, address))

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "NCU-TLDR 信箱驗證"
    msg["From"] = from_formatted
    msg["To"] = to_email
    msg["Cc"] = _CC_ADDRESS

    html_body = (
        f"<p>請點擊以下連結完成 NCU-TLDR 信箱驗證：</p>"
        f'<p><a href="{verify_url}">{verify_url}</a></p>'
        f"<p>此連結將於 24 小時後失效。</p>"
    )
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    client = _get_ses_client()
    try:
        client.send_raw_email(
            Source=from_formatted,
            Destinations=[to_email, _CC_ADDRESS],
            RawMessage={"Data": msg.as_string()},
        )
        return True
    except ClientError as exc:
        logger.error("SES send_raw_email failed: %s", exc.response["Error"])
        return False
